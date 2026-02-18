"""
Вспомогательные функции для парсера
"""
import time
import random
import logging
import re
from datetime import datetime
from decouple import config
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def fetch_url(url: str, timeout: int = 10) -> BeautifulSoup:
    """Выполняет HTTP-запрос и возвращает распарсенный HTML"""
    try:
        user_agent = config(
            'PARSER_USER_AGENT',
            default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        logger.debug(f"Запрос: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Используем html.parser вместо lxml для надёжности с "битым" HTML
        return BeautifulSoup(response.text, 'html.parser')

    except requests.RequestException as e:
        raise Exception(f"Ошибка сети {url}: {e}")
    except Exception as e:
        raise Exception(f"Ошибка парсинга {url}: {e}")


def random_delay():
    """Случайная задержка между запросами"""
    delay_min = config('PARSER_REQUEST_DELAY_MIN', default=1.0, cast=float)
    delay_max = config('PARSER_REQUEST_DELAY_MAX', default=2.5, cast=float)

    delay = random.uniform(delay_min, delay_max)
    logger.debug(f"Задержка: {delay:.2f} сек")
    time.sleep(delay)


def time_to_ms(time_str: str) -> int:
    """
    Конвертирует строку времени в миллисекунды.

    Поддерживает:
    - "28.423" → 28423
    - "01:23.456" → 83456
    - "+21.194 (28.973)" → 28973 (берём время в скобках)
    - "1:46.219" → 106219
    """
    try:
        time_str = time_str.strip()

        # Ищем время в скобках "(28.423)"
        bracket_match = re.search(r'\((\d+[:.]\d+)\)', time_str)
        if bracket_match:
            time_str = bracket_match.group(1)

        # Убираем отставание "+21.194"
        time_str = re.sub(r'\+[\d.]+\s*', '', time_str).split()[0]

        if ':' in time_str:
            # Формат "01:23.456"
            minutes, rest = time_str.split(':')
            if '.' in rest:
                seconds, ms = rest.split('.')
            else:
                seconds, ms = rest, '0'
            return int(minutes) * 60_000 + int(seconds) * 1000 + int(ms.ljust(3, '0')[:3])
        else:
            # Формат "28.423"
            if '.' in time_str:
                seconds, ms = time_str.split('.')
            else:
                seconds, ms = time_str, '0'
            return int(seconds) * 1000 + int(ms.ljust(3, '0')[:3])
    except:
        return 0