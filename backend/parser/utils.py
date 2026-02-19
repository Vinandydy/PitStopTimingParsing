import logging
import time
import random
import re
from datetime import datetime, timedelta
from decouple import config
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def fetch_url(url: str, timeout: int = 10) -> BeautifulSoup:
    """Выполняет HTTP-запрос и возвращает распарсенный HTML"""
    user_agent = config(
        'PARSER_USER_AGENT',
        default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    return BeautifulSoup(response.text, 'html.parser')


def random_delay():
    """Случайная задержка между запросами"""
    delay_min = config('PARSER_REQUEST_DELAY_MIN', default=1.0, cast=float)
    delay_max = config('PARSER_REQUEST_DELAY_MAX', default=2.5, cast=float)
    time.sleep(random.uniform(delay_min, delay_max))


def time_to_ms(time_str: str) -> int:
    """Конвертирует время в миллисекунды: '28.423' → 28423, '01:23.456' → 83456"""
    try:
        # Убираем всё лишнее: отставание "+21.194", скобки, пробелы
        time_str = re.sub(r'\+[\d.]+\s*', '', time_str)
        time_str = re.sub(r'[()]', '', time_str).strip()
        time_str = time_str.split()[0]

        if ':' in time_str:
            minutes, rest = time_str.split(':')
            seconds, ms = rest.split('.') if '.' in rest else (rest, '0')
            return int(minutes) * 60_000 + int(seconds) * 1000 + int(ms.ljust(3, '0')[:3])
        else:
            seconds, ms = time_str.split('.') if '.' in time_str else (time_str, '0')
            return int(seconds) * 1000 + int(ms.ljust(3, '0')[:3])
    except:
        return 0


def parse_date(date_text: str, time_text: str) -> datetime:
    """Парсит дату и время из текста 'Feb 17' и '22:09'"""
    now = datetime.now()
    month_map = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
                'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

    try:
        month_abbr, day = date_text.split()
        hour, minute = map(int, time_text.split(':'))
        year = now.year

        # Определяем год
        candidate = datetime(year, month_map[month_abbr], int(day))
        if candidate > now.replace(tzinfo=None) + timedelta(days=30):
            year -= 1
        elif candidate < now.replace(tzinfo=None) - timedelta(days=300):
            year += 1

        return datetime(year, month_map[month_abbr], int(day), hour, minute)
    except:
        return now