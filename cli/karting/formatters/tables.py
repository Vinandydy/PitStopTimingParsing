"""Форматирование таблиц через rich."""

from typing import List, Dict, Any
from rich.table import Table
from rich.text import Text

from karting.utils import format_date, ms_to_formatted, session_icon, format_position


def render_heats_table(heats: List[Dict[str, Any]], title: str = "Заезды") -> Table:
    table = Table(title=title, show_lines=True, caption="💡 karting heats detail <id>")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Дата", width=12)
    table.add_column("Тип", width=8)
    table.add_column("Чемпионат", width=10)
    table.add_column("Название", style="bold")
    table.add_column("Трек", style="cyan")
    table.add_column("Круги", justify="right")

    for h in heats:
        table.add_row(
            str(h['id']),
            format_date(h['scheduled_at'], short=True),
            f"{session_icon(h.get('session_type'))} {h.get('session_type', '')[:4]}",
            h.get('championship') or '—',
            h['name'][:30] + ('…' if len(h['name']) > 30 else ''),
            h.get('track_name', '—'),
            str(h.get('laps_count', '—')),
        )
    return table

def render_results_table(results: list, title: str = "Результаты") -> Table:
    """Таблица результатов с защитой от None значений."""

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Место", justify="right", width=6)
    table.add_column("Пилот", style="bold", width=25)
    table.add_column("Карт", justify="right", width=6)
    table.add_column("Лучший", width=12)
    table.add_column("Средний", width=12)
    table.add_column("Круги", justify="right", width=7)

    for r in results:
        # Защита от None
        pos = r.get('position', 0)
        pos_style = "gold1" if pos == 1 else "silver" if pos == 2 else "bronze" if pos == 3 else ""

        best_lap = r.get('best_lap_formatted') or ms_to_formatted(r.get('best_lap_ms', 0))
        avg_lap = r.get('avg_lap_formatted') or ms_to_formatted(r.get('avg_lap_ms', 0))

        table.add_row(
            Text(str(pos), style=pos_style),
            r.get('driver_name') or '—',
            str(r.get('kart_number') or '—'),
            best_lap,
            avg_lap,
            str(r.get('laps_completed') or '—'),
        )

    return table


def render_drivers_table(drivers: List[Dict[str, Any]], title: str = "Пилоты") -> Table:
    table = Table(title=title, show_lines=True)
    table.add_column("ID", style="dim", width=6)
    table.add_column("Имя", style="bold")
    table.add_column("Команда", width=15)
    table.add_column("Заездов", justify="right")
    table.add_column("Лучший круг", width=12)

    for d in drivers:
        table.add_row(
            str(d['id']),
            d.get('name', '—'),
            d.get('team', '—'),
            str(d.get('total_races', 0)),
            ms_to_formatted(d.get('best_lap_ms', 0)),
        )
    return table