"""
Django management command для парсинга данных трека.

Использование:
    python manage.py parse_track premium
    python manage.py parse_track premium --full
    python manage.py parse_track premium --heats-only
    python manage.py parse_track premium --drivers-only
    python manage.py parse_track premium --karts-only
"""
import logging
from datetime import datetime
from typing import Optional

from django.core.management.base import BaseCommand, CommandError

from backend.core.models import Track, Kart, Driver, Heat, HeatParticipation
from backend.parser.exceptions import ParserError, ParsingError
from backend.parser.utils import (
    fetch_url,
    random_delay,
    time_to_ms,
    ms_to_time,
    parse_datetime
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Парсинг данных трека с timing.batyrshin.name'

    def add_arguments(self, parser):
        parser.add_argument(
            'track_slug',
            type=str,
            help='Слаг трека (например: premium)'
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Полный парсинг (все данные, включая перепарсинг существующих)'
        )
        parser.add_argument(
            '--heats-only',
            action='store_true',
            help='Парсить только заезды'
        )
        parser.add_argument(
            '--drivers-only',
            action='store_true',
            help='Парсить только гонщиков'
        )
        parser.add_argument(
            '--karts-only',
            action='store_true',
            help='Парсить только карты'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Лимит страниц для парсинга (для тестирования)'
        )

    def handle(self, *args, **options):
        track_slug = options['track_slug']
        is_full = options['full']
        heats_only = options['heats_only']
        drivers_only = options['drivers_only']
        karts_only = options['karts_only']
        limit = options['limit']

        try:
            self.stdout.write(f"Начинаем парсинг трека: {track_slug}")
            logger.info(f"Начинаем парсинг трека: {track_slug}")

            # Получаем или создаём трек
            track, created = Track.objects.get_or_create(
                slug=track_slug,
                defaults={'name': track_slug.capitalize()}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан новый трек: {track.name}"))
            else:
                self.stdout.write(f"Используем существующий трек: {track.name}")

            # Парсим данные в зависимости от опций
            if not any([heats_only, drivers_only, karts_only]):
                # Парсим всё
                self.parse_karts(track, is_full)
                random_delay()
                self.parse_drivers(track, is_full)
                random_delay()
                self.parse_heats(track, is_full, limit)
            else:
                # Парсим только выбранное
                if karts_only or not any([heats_only, drivers_only]):
                    self.parse_karts(track, is_full)
                    random_delay()
                if drivers_only or not any([heats_only, karts_only]):
                    self.parse_drivers(track, is_full)
                    random_delay()
                if heats_only or not any([drivers_only, karts_only]):
                    self.parse_heats(track, is_full, limit)

            self.stdout.write(self.style.SUCCESS(
                f"Парсинг трека {track_slug} завершён успешно!"
            ))
            logger.info(f"Парсинг трека {track_slug} завершён успешно!")

        except ParserError as e:
            logger.error(f"Ошибка парсера: {e}")
            raise CommandError(f"Ошибка парсера: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
            raise CommandError(f"Неожиданная ошибка: {e}")

    def parse_karts(self, track: Track, force_update: bool = False):
        """Парсит список картов трека"""
        self.stdout.write(f"\nПарсим карты трека {track.slug}...")
        logger.info(f"Парсим карты трека {track.slug}...")

        url = f"https://timing.batyrshin.name/tracks/{track.slug}/karts"

        try:
            soup = fetch_url(url)

            # Находим таблицу картов
            table = soup.find('table', class_='table')
            if not table:
                raise ParsingError(f"Не найдена таблица картов на {url}")

            tbody = table.find('tbody')
            if not tbody:
                raise ParsingError(f"Не найден tbody в таблице картов на {url}")

            rows = tbody.find_all('tr')
            if not rows:
                self.stdout.write(self.style.WARNING("Карты не найдены"))
                return

            created_count = 0
            updated_count = 0

            for row in rows:
                try:
                    # Извлекаем данные из строки
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue

                    # Номер карты
                    kart_number_cell = cells[0]
                    kart_number = int(kart_number_cell.text.strip())

                    # Статус (активен/неактивен)
                    status_badge = row.find('span', class_='badge')
                    is_active = status_badge and 'success' in status_badge.get('class', [])

                    # Сохраняем в БД
                    kart, created = Kart.objects.update_or_create(
                        track=track,
                        number=kart_number,
                        defaults={'is_active': is_active}
                    )

                    if created:
                        created_count += 1
                        logger.debug(f"Создан карт #{kart_number}")
                    else:
                        if kart.is_active != is_active or force_update:
                            kart.is_active = is_active
                            kart.save()
                            updated_count += 1
                            logger.debug(f"Обновлён карт #{kart_number}")

                except (ValueError, AttributeError) as e:
                    logger.warning(f"Ошибка парсинга строки картов: {e}")
                    continue

            self.stdout.write(self.style.SUCCESS(
                f"Карты: {created_count} создано, {updated_count} обновлено"
            ))

        except Exception as e:
            logger.error(f"Ошибка при парсинге картов: {e}")
            raise

    def parse_drivers(self, track: Track, force_update: bool = False):
        """Парсит список гонщиков трека"""
        self.stdout.write(f"\nПарсим гонщиков трека {track.slug}...")
        logger.info(f"Парсим гонщиков трека {track.slug}...")

        url = f"https://timing.batyrshin.name/tracks/{track.slug}/drivers"

        try:
            soup = fetch_url(url)

            # Находим таблицу гонщиков
            table = soup.find('table', class_='table')
            if not table:
                raise ParsingError(f"Не найдена таблица гонщиков на {url}")

            tbody = table.find('tbody')
            if not tbody:
                raise ParsingError(f"Не найден tbody в таблице гонщиков на {url}")

            rows = tbody.find_all('tr')
            if not rows:
                self.stdout.write(self.style.WARNING("Гонщики не найдены"))
                return

            created_count = 0
            updated_count = 0

            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue

                    # Внешний ID из ссылки
                    driver_link = row.find('a', href=True)
                    if not driver_link:
                        continue

                    href = driver_link['href']
                    # /tracks/premium/drivers/159315
                    external_id = int(href.split('/')[-1])

                    # Имя гонщика
                    name = cells[1].text.strip()

                    # Команда (если есть)
                    team = cells[2].text.strip() if len(cells) > 2 else ''

                    # Сохраняем в БД
                    driver, created = Driver.objects.update_or_create(
                        external_id=external_id,
                        defaults={
                            'track': track,
                            'name': name,
                            'team': team
                        }
                    )

                    if created:
                        created_count += 1
                        logger.debug(f"Создан гонщик {name} (ID: {external_id})")
                    else:
                        if force_update:
                            driver.track = track
                            driver.name = name
                            driver.team = team
                            driver.save()
                            updated_count += 1
                            logger.debug(f"Обновлён гонщик {name} (ID: {external_id})")

                except (ValueError, AttributeError) as e:
                    logger.warning(f"Ошибка парсинга строки гонщиков: {e}")
                    continue

            self.stdout.write(self.style.SUCCESS(
                f"Гонщики: {created_count} создано, {updated_count} обновлено"
            ))

        except Exception as e:
            logger.error(f"Ошибка при парсинге гонщиков: {e}")
            raise

    def parse_heats(self, track: Track, force_update: bool = False, limit: Optional[int] = None):
        """Парсит список заездов трека с пагинацией"""
        self.stdout.write(f"\nПарсим заезды трека {track.slug}...")
        logger.info(f"Парсим заезды трека {track.slug}...")

        page = 1
        total_heats = 0
        new_heats = 0

        while True:
            url = f"https://timing.batyrshin.name/tracks/{track.slug}/heats?page={page}"

            try:
                soup = fetch_url(url)

                # Находим таблицу заездов
                table = soup.find('table', class_='table')
                if not table:
                    if page == 1:
                        raise ParsingError(f"Не найдена таблица заездов на {url}")
                    break  # Больше страниц нет

                tbody = table.find('tbody')
                if not tbody:
                    break

                rows = tbody.find_all('tr')
                if not rows:
                    break

                self.stdout.write(f"  Страница {page}: {len(rows)} заездов")
                logger.info(f"Страница {page}: {len(rows)} заездов")

                for row in rows:
                    try:
                        self._parse_heat_row(track, row, force_update)
                        total_heats += 1

                    except Exception as e:
                        logger.warning(f"Ошибка парсинга заезда: {e}")
                        continue

                # Проверяем наличие следующей страницы
                pagination = soup.find('ul', class_='pagination')
                if pagination:
                    next_link = pagination.find('a', string='»')
                    if not next_link:
                        break
                else:
                    break

                page += 1
                if limit and page > limit:
                    self.stdout.write(self.style.WARNING(f"Достигнут лимит страниц: {limit}"))
                    break

                # Задержка между страницами
                random_delay()

            except Exception as e:
                logger.error(f"Ошибка при парсинге страницы {page}: {e}")
                break

        self.stdout.write(self.style.SUCCESS(
            f"Заезды: {total_heats} обработано"
        ))

    def _parse_heat_row(self, track: Track, row, force_update: bool):
        """Парсит одну строку заезда из таблицы"""
        cells = row.find_all('td')
        if len(cells) < 3:
            return

        # Ссылка на заезд
        heat_link = row.find('a', href=True)
        if not heat_link:
            return

        href = heat_link['href']
        # /tracks/premium/heats/105535
        external_id = int(href.split('/')[-1])

        # Проверяем, существует ли уже такой заезд
        if not force_update:
            if Heat.objects.filter(external_id=external_id, track=track).exists():
                logger.debug(f"Заезд {external_id} уже существует, пропускаем")
                return

        # Дата и время
        datetime_cell = cells[0]
        datetime_text = datetime_cell.text.strip()

        # Разбиваем на дату и время
        parts = datetime_text.split()
        if len(parts) >= 2:
            date_str = parts[0]  # 12.02.2026
            time_str = parts[1]  # 15:30
            scheduled_at = parse_datetime(date_str, time_str)
        else:
            scheduled_at = datetime.now()

        # Название заезда
        name = heat_link.text.strip() if heat_link.text else ''

        # Количество кругов (если есть)
        laps_count = 0
        if len(cells) > 2:
            laps_text = cells[2].text.strip()
            try:
                laps_count = int(laps_text)
            except (ValueError, TypeError):
                pass

        # Сохраняем заезд
        heat, created = Heat.objects.update_or_create(
            external_id=external_id,
            track=track,
            defaults={
                'scheduled_at': scheduled_at,
                'name': name,
                'laps_count': laps_count
            }
        )

        if created:
            logger.info(f"Создан заезд {external_id}: {name}")
        else:
            logger.info(f"Обновлён заезд {external_id}: {name}")

        # Парсим детали заезда (результаты)
        self._parse_heat_details(heat, track.slug)

        # Задержка после парсинга деталей заезда
        random_delay()

    def _parse_heat_details(self, heat: Heat, track_slug: str):
        """Парсит детали конкретного заезда (результаты)"""
        url = f"https://timing.batyrshin.name/tracks/{track_slug}/heats/{heat.external_id}"

        try:
            soup = fetch_url(url)

            # Находим таблицу результатов
            table = soup.find('table', id='results')
            if not table:
                logger.warning(f"Не найдена таблица результатов для заезда {heat.external_id}")
                return

            tbody = table.find('tbody')
            if not tbody:
                return

            rows = tbody.find_all('tr')
            if not rows:
                logger.warning(f"Нет результатов для заезда {heat.external_id}")
                return

            results_created = 0

            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) < 4:
                        continue

                    # Позиция
                    position_text = cells[0].text.strip()
                    try:
                        position = int(position_text)
                    except (ValueError, TypeError):
                        continue

                    # Гонщик
                    driver_link = cells[1].find('a', href=True)
                    if not driver_link:
                        continue

                    driver_href = driver_link['href']
                    driver_id = int(driver_href.split('/')[-1])

                    # Получаем или создаём гонщика (если ещё не существует)
                    driver, _ = Driver.objects.get_or_create(
                        external_id=driver_id,
                        defaults={
                            'track': heat.track,
                            'name': driver_link.text.strip()
                        }
                    )

                    # Карт
                    kart_link = cells[2].find('a', href=True)
                    if not kart_link:
                        continue

                    kart_number_text = kart_link.text.strip()
                    try:
                        kart_number = int(kart_number_text)
                    except (ValueError, TypeError):
                        continue

                    # Получаем или создаём карт
                    kart, _ = Kart.objects.get_or_create(
                        track=heat.track,
                        number=kart_number,
                        defaults={'is_active': True}
                    )

                    # Лучшее время
                    best_lap_text = cells[3].text.strip()
                    best_lap_ms = time_to_ms(best_lap_text)

                    # Общее время и количество кругов (если есть)
                    total_time_ms = None
                    laps_completed = 0

                    if len(cells) > 5:
                        laps_text = cells[5].text.strip()
                        try:
                            laps_completed = int(laps_text)
                        except (ValueError, TypeError):
                            pass

                    # Сохраняем результат
                    participation, created = HeatParticipation.objects.update_or_create(
                        heat=heat,
                        driver=driver,
                        defaults={
                            'kart': kart,
                            'position': position,
                            'best_lap_ms': best_lap_ms,
                            'total_time_ms': total_time_ms,
                            'laps_completed': laps_completed
                        }
                    )

                    if created:
                        results_created += 1
                        logger.debug(
                            f"Результат: {driver.name} - {position} место, "
                            f"лучший круг: {ms_to_time(best_lap_ms)}"
                        )

                except Exception as e:
                    logger.warning(f"Ошибка парсинга результата: {e}")
                    continue

            logger.info(f"Заезд {heat.external_id}: {results_created} результатов сохранено")

        except Exception as e:
            logger.error(f"Ошибка при парсинге деталей заезда {heat.external_id}: {e}")
            raise