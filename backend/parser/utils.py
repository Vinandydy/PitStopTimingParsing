"""Вспомогательные функции для парсера"""
import time
import random
import logging
from datetime import datetime, timedelta
from decouple import config
import requests
from bs4 import BeautifulSoup
from parser.exceptions import *

logger = logging.getLogger(__name__)


def time_to_ms(time_str: str) -> int:
    """
    Конвертирует строку времени в миллисекунды.

    Args:
        time_str: Строка в формате "01:23.456" или "1:23.456"

    Returns:
        Количество миллисекунд

    Raises:
        ValueError: Если формат времени некорректен
    """
    try:
        # Убираем лишние пробелы
        time_str = time_str.strip()

        # Разбиваем на минуты и секунды
        if ':' in time_str:
            minutes_part, seconds_part = time_str.split(':')
            minutes = int(minutes_part)
        else:
            minutes = 0
            seconds_part = time_str

        # Разбиваем секунды на целую часть и миллисекунды
        if '.' in seconds_part:
            seconds, ms = seconds_part.split('.')
        else:
            seconds = seconds_part
            ms = '0'

        seconds = int(seconds)
        ms = int(ms.ljust(3, '0')[:3])  # Дополняем до 3 цифр

        total_ms = minutes * 60_000 + seconds * 1000 + ms
        return total_ms

    except (ValueError, AttributeError) as e:
        logger.warning(f"Ошибка парсинга времени '{time_str}': {e}")
        return 0


def ms_to_time(ms: int) -> str:
    """
    Конвертирует миллисекунды в строку времени.

    Args:
        ms: Количество миллисекунд

    Returns:
        Строка в формате "01:23.456"
    """
    minutes = ms // 60_000
    seconds = (ms % 60_000) // 1000
    milliseconds = ms % 1000

    return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def fetch_url(url: str, timeout: int = 10) -> BeautifulSoup:
    """
    Выполняет HTTP-запрос и возвращает распарсенный HTML.

    Args:
        url: URL для запроса
        timeout: Таймаут запроса в секундах

    Returns:
        BeautifulSoup объект

    Raises:
        NetworkError: При ошибке сети
        ParsingError: При ошибке парсинга HTML
    """
    try:
        # Получаем параметры из .env
        user_agent = config(
            'PARSER_USER_AGENT',
            default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        logger.debug(f"Запрос к {url}")

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Проверяем, что получили HTML
        content_type = response.headers.get('Content-Type', '')
        if 'html' not in content_type.lower():
            raise ParsingError(f"Некорректный тип контента: {content_type}")

        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    except requests.RequestException as e:
        raise NetworkError(f"Ошибка сети при запросе {url}: {e}")
    except Exception as e:
        raise ParsingError(f"Ошибка парсинга HTML {url}: {e}")


def random_delay():
    """Случайная задержка между запросами для защиты от блокировок"""
    delay_min = config('PARSER_REQUEST_DELAY_MIN', default=1.0, cast=float)
    delay_max = config('PARSER_REQUEST_DELAY_MAX', default=2.5, cast=float)

    delay = random.uniform(delay_min, delay_max)
    logger.debug(f"Задержка между запросами: {delay:.2f} сек")
    time.sleep(delay)


def parse_datetime(date_str: str, time_str: str) -> datetime:
    """
    Парсит дату и время из строки.

    Args:
        date_str: Строка даты (например, "12.02.2026")
        time_str: Строка времени (например, "15:30")

    Returns:
        datetime объект

    Raises:
        ValueError: Если формат даты/времени некорректен
    """
    try:
        # Парсим дату
        date_obj = datetime.strptime(date_str.strip(), '%d.%m.%Y')

        # Парсим время
        time_obj = datetime.strptime(time_str.strip(), '%H:%M')

        # Объединяем
        result = datetime.combine(date_obj.date(), time_obj.time())
        return result

    except ValueError as e:
        logger.warning(f"Ошибка парсинга даты '{date_str} {time_str}': {e}")
        # Возвращаем текущее время как фоллбэк
        return datetime.now()


def get_period_dates(period: str) -> tuple[datetime, datetime]:
    """
    Возвращает даты начала и конца периода.

    Args:
        period: Период ('7d', '30d', 'all')

    Returns:
        Кортеж (начало, конец)
    """
    now = datetime.now()

    if period == '7d':
        start = now - timedelta(days=7)
    elif period == '30d':
        start = now - timedelta(days=30)
    elif period == '90d':
        start = now - timedelta(days=90)
    else:  # 'all' или неизвестный
        start = datetime(2000, 1, 1)  # Очень старая дата

    return start, now