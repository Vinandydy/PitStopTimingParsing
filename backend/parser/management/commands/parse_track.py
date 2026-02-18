import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from bs4 import BeautifulSoup
from core.models import Track, Heat, Driver, Kart, HeatParticipation
from parser.utils import fetch_url


class Command(BaseCommand):
    help = 'Парсит заезды трека Premium'

    def handle(self, *args, **options):
        track, _ = Track.objects.get_or_create(slug='premium', defaults={'name': 'Premium'})

        # Шаг 1: Получаем список заездов
        self.stdout.write("Получаем список заездов...")
        url = "https://timing.batyrshin.name/tracks/premium/heats?page=1"
        soup = fetch_url(url)

        # Находим все ссылки на заезды
        heat_links = soup.select('a[href*="/tracks/premium/heats/"]')
        self.stdout.write(f"Найдено {len(heat_links)} заездов")

        processed = 0
        for link in heat_links:
            try:
                # Извлекаем ID и название
                href = link['href']
                heat_id = int(href.split('/')[-1])
                heat_name = link.text.strip()

                # Пропускаем "Заезд XX"
                if re.match(r'^Заезд \d+', heat_name):
                    continue

                # Проверяем существование в БД
                if Heat.objects.filter(external_id=heat_id, track=track).exists():
                    continue

                # Шаг 2: Парсим детальную страницу
                detail_url = f"https://timing.batyrshin.name{href}"
                detail_soup = fetch_url(detail_url)

                # Извлекаем данные заезда
                heat_data = self.extract_heat_data(detail_soup, heat_id, heat_name, track)
                if not heat_data:
                    continue

                # Сохраняем заезд
                heat = Heat.objects.create(**heat_data)

                # Извлекаем результаты
                results = self.extract_results(detail_soup, heat, track)
                for res in results:
                    HeatParticipation.objects.create(**res)

                processed += 1
                self.stdout.write(f"✅ {heat_name} (ID: {heat_id})")

            except Exception as e:
                self.stdout.write(f"❌ Ошибка заезда: {e}")
                continue

        self.stdout.write(self.style.SUCCESS(f"Обработано {processed} новых заездов"))

    def extract_heat_data(self, soup, heat_id, heat_name, track):
        """Извлекает метаданные заезда"""
        try:
            # Дата и время (формат: "17 Feb 2026, 22:09")
            date_time_elem = soup.find(string=lambda t: t and ', ' in t and ':' in t)
            if date_time_elem:
                parts = date_time_elem.strip().split(', ')
                date_part, time_part = parts[0], parts[1]
                day, month_abbr, year = date_part.split()
                hour, minute = time_part.split(':')

                month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                             'Oct': 10, 'Nov': 11, 'Dec': 12}
                scheduled_at = timezone.make_aware(datetime(
                    int(year), month_map[month_abbr], int(day), int(hour), int(minute)
                ))
            else:
                scheduled_at = timezone.now()

            return {
                'external_id': heat_id,
                'track': track,
                'name': heat_name,
                'scheduled_at': scheduled_at,
                'laps_count': 0
            }
        except:
            return None

    def extract_results(self, soup, heat, track):
        """Извлекает результаты заезда из таблицы #results"""
        table = soup.select_one('table#results')
        if not table:
            return []

        rows = table.select('tr')
        if len(rows) < 3:
            return []

        # Извлекаем имена гонщиков
        driver_cells = rows[1].select('td,th')[1:]
        drivers = []
        for cell in driver_cells:
            link = cell.select_one('a[href*="/drivers/"]')
            if link:
                name = link.text.strip()
                external_id = int(link['href'].split('/')[-1])
                driver, _ = Driver.objects.get_or_create(
                    external_id=external_id,
                    defaults={'track': track, 'name': name}
                )
            else:
                name = cell.text.strip()
                driver, _ = Driver.objects.get_or_create(
                    name=name,
                    track=track,
                    defaults={'external_id': -heat.external_id * 1000 - len(drivers)}
                )
            drivers.append(driver)

        # Извлекаем номера картов
        kart_cells = rows[2].select('td,th')[1:]
        karts = []
        for cell in kart_cells:
            link = cell.select_one('a[href*="/karts/"]')
            if link:
                try:
                    number = int(link.text.strip())
                    kart, _ = Kart.objects.get_or_create(
                        track=track,
                        number=number,
                        defaults={'is_active': True}
                    )
                except:
                    kart, _ = Kart.objects.get_or_create(
                        track=track,
                        number=999,
                        defaults={'is_active': False}
                    )
            else:
                kart, _ = Kart.objects.get_or_create(
                    track=track,
                    number=999,
                    defaults={'is_active': False}
                )
            karts.append(kart)

        # Извлекаем лучшее время из строки "Best"
        best_row = None
        for row in rows:
            if row.select_one('td,th') and 'Best' in row.select_one('td,th').text:
                best_row = row
                break

        results = []
        for i, driver in enumerate(drivers):
            best_lap_ms = 0
            if best_row and len(best_row.select('td,th')) > i + 1:
                time_text = best_row.select('td,th')[i + 1].text.strip()
                best_lap_ms = self.time_to_ms(time_text)

            results.append({
                'heat': heat,
                'driver': driver,
                'kart': karts[i] if i < len(karts) else karts[-1],
                'position': i + 1,
                'best_lap_ms': best_lap_ms,
                'laps_completed': 0
            })

        return results

    def time_to_ms(self, time_str):
        """Конвертирует время в миллисекунды"""
        try:
            time_str = re.sub(r'[()]', '', time_str).split()[0]
            if ':' in time_str:
                minutes, rest = time_str.split(':')
                seconds, ms = rest.split('.') if '.' in rest else (rest, '0')
                return int(minutes) * 60_000 + int(seconds) * 1000 + int(ms.ljust(3, '0')[:3])
            else:
                seconds, ms = time_str.split('.') if '.' in time_str else (time_str, '0')
                return int(seconds) * 1000 + int(ms.ljust(3, '0')[:3])
        except:
            return 0