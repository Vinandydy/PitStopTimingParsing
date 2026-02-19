import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from bs4 import BeautifulSoup

from core.models import Track, Heat, Driver, Kart, HeatParticipation
from parser.utils import fetch_url, random_delay, time_to_ms, parse_date


class Command(BaseCommand):
    help = 'Парсит данные трека Premium с timing.batyrshin.name'

    def add_arguments(self, parser):
        parser.add_argument('--pages', type=int, default=1, help='Количество страниц для парсинга')

    def handle(self, *args, **options):
        track_slug = 'premium'
        track, _ = Track.objects.get_or_create(slug=track_slug, defaults={'name': 'Premium'})

        self.stdout.write("Парсим справочники...")
        self.parse_karts(track)
        self.parse_drivers(track)

        self.stdout.write("Парсим заезды...")
        self.parse_heats(track, options['pages'])

        self.stdout.write(self.style.SUCCESS("✅ Парсинг завершён"))

    def parse_karts(self, track):
        soup = fetch_url(f"https://timing.batyrshin.name/tracks/{track.slug}/karts")
        rows = soup.select('table.table tbody tr')
        for row in rows:
            try:
                number = int(row.select_one('td').text.strip())
                badge = row.select_one('span.badge')
                is_active = badge and 'bg-success' in badge.get('class', [])
                Kart.objects.update_or_create(track=track, number=number, defaults={'is_active': is_active})
            except:
                pass
        self.stdout.write(f"✅ Карты: {len(rows)}")

    def parse_drivers(self, track):
        soup = fetch_url(f"https://timing.batyrshin.name/tracks/{track.slug}/drivers")
        rows = soup.select('table.table tbody tr')
        for row in rows:
            try:
                link = row.select_one('a[href*="/drivers/"]')
                if not link: continue
                external_id = int(link['href'].split('/')[-1])
                name = row.select('td')[1].text.strip()
                team = row.select('td')[2].text.strip() if len(row.select('td')) > 2 else ''
                Driver.objects.update_or_create(external_id=external_id,
                                                defaults={'track': track, 'name': name, 'team': team})
            except:
                pass
        self.stdout.write(f"✅ Гонщики: {len(rows)}")

    def parse_heats(self, track, pages):
        total_heats = 0
        total_results = 0

        for page in range(1, pages + 1):
            url = f"https://timing.batyrshin.name/tracks/{track.slug}/heats?page={page}"
            soup = fetch_url(url)

            # Ищем ВСЕ ссылки, содержащие "/heats/" (без привязки к треку!)
            heat_links = soup.find_all('a',
                                       href=lambda href: href and '/heats/' in href and href.split('/')[-1].isdigit())

            if not heat_links:
                self.stdout.write(self.style.WARNING(f"  Страница {page}: ссылки на заезды не найдены"))
                break

            self.stdout.write(f"  Страница {page}: найдено {len(heat_links)} ссылок на заезды")

            current_date = None
            heats_processed = 0

            for link in heat_links:
                try:
                    href = link['href']
                    # Извлекаем ID из последней части URL (например, "/heats/106086" → "106086")
                    heat_id = int(href.split('/')[-1])
                    heat_name = link.text.strip()

                    # Игнорируем ненужные заезды
                    if re.match(r'^(Дети|ДЕТИ|дети|Заезд \d+|Заезд \d+ дети|Заезд \d+ дети)$', heat_name, re.I):
                        continue

                    # Находим дату (ближайший предыдущий текст "Feb 17")
                    prev_text = link.find_previous(
                        string=lambda t: t and re.match(r'^[A-Z][a-z]{2} \d{1,2}$', t.strip()))
                    if prev_text:
                        current_date = prev_text.strip()

                    # Находим время (следующий текст "22:09" после ссылки)
                    next_text = link.find_next(string=lambda t: t and re.match(r'^\d{1,2}:\d{2}$', t.strip()))
                    time_text = next_text.strip() if next_text else "00:00"

                    # Парсим дату и время
                    if current_date:
                        scheduled_at = timezone.make_aware(
                            parse_date(current_date, time_text),
                            timezone.get_current_timezone()
                        )
                    else:
                        scheduled_at = timezone.now()

                    # Определяем тип сессии
                    session_type = ''
                    if 'гонка' in heat_name.lower() or 'race' in heat_name.lower():
                        session_type = 'Race'
                    elif 'квалификация' in heat_name.lower() or 'qual' in heat_name.lower():
                        session_type = 'Qualification'
                    elif 'тренировка' in heat_name.lower() or 'тепл' in heat_name.lower() or 'warm' in heat_name.lower():
                        session_type = 'Practice'

                    # Определяем чемпионат (только если явно указан в блоке)
                    championship = ''
                    # Ищем блок чемпионата рядом с заездом
                    champ_block = link.find_next(string=lambda t: t and 'ГГ2026' in t)
                    if champ_block or 'ГГ2026' in heat_name:
                        championship = 'ГГ2026'
                    elif 'OPEN2025' in heat_name:
                        championship = 'OPEN2025'

                    # Сохраняем заезд
                    heat, created = Heat.objects.update_or_create(
                        external_id=heat_id,
                        track=track,
                        defaults={
                            'name': heat_name,
                            'scheduled_at': scheduled_at,
                            'session_type': session_type,
                            'championship': championship,
                            'laps_count': 0
                        }
                    )

                    if not created:
                        continue

                    # Парсим детальную страницу
                    results_count = self.parse_heat_details(heat, track.slug)
                    total_results += results_count
                    heats_processed += 1
                    total_heats += 1

                    self.stdout.write(f"    🏁 {heat_name} (ID: {heat_id}) - {results_count} результатов")
                    random_delay()

                except Exception as e:
                    self.stdout.write(f"    ❌ Ошибка заезда: {e}")
                    continue

            self.stdout.write(f"  Страница {page}: обработано {heats_processed} заездов")

            # Проверяем пагинацию
            if not soup.select_one('a:-soup-contains("Next"), a:-soup-contains("»")'):
                break

        self.stdout.write(f"✅ Заезды: {total_heats} обработано, {total_results} результатов")

    def parse_heat_details(self, heat, track_slug):
        """Парсит детальную страницу заезда с полной статистикой"""
        url = f"https://timing.batyrshin.name/tracks/{track_slug}/heats/{heat.external_id}"
        soup = fetch_url(url)

        # Находим таблицу результатов (ищем по наличию строки "Driver")
        table = None
        for tbl in soup.find_all('table'):
            if tbl.find(string=lambda t: t and 'Driver' in t):
                table = tbl
                break

        if not table:
            self.stdout.write(f"    ⚠️ Таблица результатов не найдена для заезда {heat.external_id}")
            return 0

        rows = table.find_all('tr')
        if len(rows) < 5:
            self.stdout.write(f"    ⚠️ Недостаточно строк в таблице заезда {heat.external_id}")
            return 0

        # Словарь для хранения данных по позициям (индекс = позиция - 1)
        data = {
            'drivers': [],  # Имена гонщиков
            'driver_ids': [],  # external_id гонщиков
            'karts': [],  # Номера картов
            'best_laps': [],  # Лучшие времена (мс)
            'avg_laps': [],  # Средние времена (мс)
            'dev_laps': [],  # Отклонение (мс)
            's1_laps': [],  # Круги в сессии S1
            's1_best': [],  # Лучшее время в S1 (мс)
            's2_laps': [],
            's2_best': [],
            's3_laps': [],
            's3_best': [],
        }

        # Проходим по строкам и определяем их тип
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue

            first_cell = cells[0]
            first_text = first_cell.get_text(strip=True)

            # Строка "Driver" — имена гонщиков
            if 'Driver' in first_text:
                for cell in cells[1:]:
                    link = cell.find('a', href=lambda h: h and '/drivers/' in h)
                    if link:
                        driver_name = link.get_text(strip=True)
                        driver_id = int(link['href'].split('/')[-1])
                        data['drivers'].append(driver_name)
                        data['driver_ids'].append(driver_id)
                    else:
                        data['drivers'].append(cell.get_text(strip=True))
                        data['driver_ids'].append(None)

            # Строка "Kart" — номера картов
            elif 'Kart' in first_text:
                for cell in cells[1:]:
                    link = cell.find('a', href=lambda h: h and '/karts/' in h)
                    if link:
                        try:
                            kart_number = int(link.get_text(strip=True))
                            data['karts'].append(kart_number)
                        except:
                            data['karts'].append(999)
                    else:
                        try:
                            kart_number = int(cell.get_text(strip=True))
                            data['karts'].append(kart_number)
                        except:
                            data['karts'].append(999)

            # Строка "Best" — лучшие времена
            elif 'Best' in first_text:
                for i, cell in enumerate(cells[1:]):
                    time_ms = time_to_ms(cell.get_text())
                    if i < len(data['best_laps']):
                        data['best_laps'][i] = time_ms
                    else:
                        data['best_laps'].append(time_ms)

            # Строка "Avg" — средние времена
            elif 'Avg' in first_text:
                for i, cell in enumerate(cells[1:]):
                    time_ms = time_to_ms(cell.get_text())
                    if i < len(data['avg_laps']):
                        data['avg_laps'][i] = time_ms
                    else:
                        data['avg_laps'].append(time_ms)

            # Строка "Dev" — отклонение
            elif 'Dev' in first_text:
                for i, cell in enumerate(cells[1:]):
                    time_ms = time_to_ms(cell.get_text())
                    if i < len(data['dev_laps']):
                        data['dev_laps'][i] = time_ms
                    else:
                        data['dev_laps'].append(time_ms)

            # Сессия S1
            elif 'S1 laps' in first_text:
                for i, cell in enumerate(cells[1:]):
                    laps = self._extract_number(cell.get_text())
                    if i < len(data['s1_laps']):
                        data['s1_laps'][i] = laps
                    else:
                        data['s1_laps'].append(laps)
            elif 'S1 best' in first_text:
                for i, cell in enumerate(cells[1:]):
                    time_ms = time_to_ms(cell.get_text())
                    if i < len(data['s1_best']):
                        data['s1_best'][i] = time_ms
                    else:
                        data['s1_best'].append(time_ms)

            # Сессия S2
            elif 'S2 laps' in first_text:
                for i, cell in enumerate(cells[1:]):
                    laps = self._extract_number(cell.get_text())
                    if i < len(data['s2_laps']):
                        data['s2_laps'][i] = laps
                    else:
                        data['s2_laps'].append(laps)
            elif 'S2 best' in first_text:
                for i, cell in enumerate(cells[1:]):
                    time_ms = time_to_ms(cell.get_text())
                    if i < len(data['s2_best']):
                        data['s2_best'][i] = time_ms
                    else:
                        data['s2_best'].append(time_ms)

            # Сессия S3
            elif 'S3 laps' in first_text:
                for i, cell in enumerate(cells[1:]):
                    laps = self._extract_number(cell.get_text())
                    if i < len(data['s3_laps']):
                        data['s3_laps'][i] = laps
                    else:
                        data['s3_laps'].append(laps)
            elif 'S3 best' in first_text:
                for i, cell in enumerate(cells[1:]):
                    time_ms = time_to_ms(cell.get_text())
                    if i < len(data['s3_best']):
                        data['s3_best'][i] = time_ms
                    else:
                        data['s3_best'].append(time_ms)

        # Заполняем недостающие значения нулями
        max_pos = len(data['drivers'])
        for key in ['best_laps', 'avg_laps', 'dev_laps', 's1_laps', 's1_best', 's2_laps', 's2_best', 's3_laps',
                    's3_best']:
            while len(data[key]) < max_pos:
                data[key].append(0)
        while len(data['karts']) < max_pos:
            data['karts'].append(999)

        # Сохраняем результаты
        results_count = 0
        for i in range(max_pos):
            if not data['drivers'][i] or data['drivers'][i] in ['-', '', 'Driver']:
                continue

            # Получаем/создаём гонщика
            if data['driver_ids'][i]:
                driver, _ = Driver.objects.get_or_create(
                    external_id=data['driver_ids'][i],
                    defaults={'track': heat.track, 'name': data['drivers'][i]}
                )
            else:
                driver, _ = Driver.objects.get_or_create(
                    name=data['drivers'][i],
                    track=heat.track,
                    defaults={'external_id': -heat.external_id * 1000 - i}
                )

            # Получаем/создаём карт
            kart_num = data['karts'][i] if i < len(data['karts']) else 999
            kart, _ = Kart.objects.get_or_create(
                track=heat.track,
                number=kart_num,
                defaults={'is_active': True}
            )

            # Сохраняем результат
            HeatParticipation.objects.update_or_create(
                heat=heat,
                driver=driver,
                defaults={
                    'kart': kart,
                    'position': i + 1,
                    'best_lap_ms': data['best_laps'][i] if i < len(data['best_laps']) else 0,
                    'avg_lap_ms': data['avg_laps'][i] if i < len(data['avg_laps']) else 0,
                    'dev_lap_ms': data['dev_laps'][i] if i < len(data['dev_laps']) else 0,
                    'laps_completed': data['s1_laps'][i] + data['s2_laps'][i] + data['s3_laps'][i] if i < len(
                        data['s1_laps']) else 0,
                    's1_best_ms': data['s1_best'][i] if i < len(data['s1_best']) else 0,
                    's1_laps': data['s1_laps'][i] if i < len(data['s1_laps']) else 0,
                    's2_best_ms': data['s2_best'][i] if i < len(data['s2_best']) else 0,
                    's2_laps': data['s2_laps'][i] if i < len(data['s2_laps']) else 0,
                    's3_best_ms': data['s3_best'][i] if i < len(data['s3_best']) else 0,
                    's3_laps': data['s3_laps'][i] if i < len(data['s3_laps']) else 0,
                    'gap_to_leader_ms': 0  # Можно вычислить из строки "Gap" при необходимости
                }
            )
            results_count += 1

        return results_count

    def _extract_number(self, text):
        """Извлекает число из текста, игнорируя 'l' и другие символы"""
        try:
            # Убираем 'l' (обозначение круга) и другие нечисловые символы
            text = re.sub(r'[^\d]', '', text.strip())
            return int(text) if text else 0
        except:
            return 0