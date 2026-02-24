"""Утилиты для форматирования данных из API."""

from datetime import datetime
from typing import Optional

def ms_to_formatted(ms: int) -> str:
    """Конвертирует миллисекунды в формат MM:SS.mmm."""
    if not ms or ms <= 0:
        return "—"
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}" if minutes else f"{seconds}.{milliseconds:03d}"

def format_date(dt_str: str, short: bool = False) -> str:
    """ISO 8601 → '24.02 21:30' или '24 февраля 2026, 21:30'."""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%d.%m %H:%M") if short else dt.strftime("%d %B %Y, %H:%M")
    except:
        return dt_str

def session_icon(t: str) -> str:
    """Иконка для типа сессии."""
    icons = {'Race': '🏁', 'Qualification': '⏱️', 'Practice': '🔧'}
    return icons.get(t or '', '❓')

def format_position(pos: int) -> str:
    """Форматирует позицию: 1 → '1st', 2 → '2nd'."""
    if not pos:
        return "—"
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    suffix = suffixes.get(pos % 10, 'th') if pos % 100 not in (11, 12, 13) else 'th'
    return f"{pos}{suffix}"