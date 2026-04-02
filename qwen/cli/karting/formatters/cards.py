"""Форматирование детальных карточек через rich."""

from typing import Any

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from karting.utils import format_date, format_position, session_icon


def render_heat_card(heat: dict[str, Any]) -> Panel:
    content = []

    header = Text.assemble(
        ("🏁 ", "bold"),
        (heat.get('name', 'Без названия'), "bold green"),
        "\n",
        (f"{heat.get('track_name', 'Трек')} • ", "cyan"),
        (format_date(heat['scheduled_at']), "dim"),
    )
    content.append(header)
    content.append("")

    meta = Table.grid(padding=(0, 2))
    meta.add_column(style="dim", width=15)
    meta.add_column()
    meta.add_row("Тип сессии:", f"{session_icon(heat.get('session_type'))} {heat.get('session_type') or '—'}")
    meta.add_row("Чемпионат:", heat.get('championship') or '—')
    meta.add_row("Кругов:", str(heat.get('laps_count', '—')))
    meta.add_row("Участников:", str(len(heat.get('results', []))))

    content.append(meta)

    return Panel(Group(*content), title=f"Заезд #{heat['id']}", border_style="blue", padding=(1, 2))


def render_driver_card(driver: dict[str, Any], stats: dict | None = None) -> Panel:
    content = []

    header = Text.assemble(
        ("👤 ", "bold"),
        (driver.get('name', '—'), "bold green"),
    )
    content.append(header)
    content.append("")

    meta = Table.grid(padding=(0, 2))
    meta.add_column(style="dim", width=15)
    meta.add_column()
    meta.add_row("ID:", str(driver.get('id', '—')))
    meta.add_row("Команда:", driver.get('team') or '—')
    meta.add_row("Трек:", driver.get('track_name', '—'))

    if stats:
        meta.add_row("Заездов:", str(stats.get('total_races', 0)))
        meta.add_row("Лучшая позиция:", format_position(stats.get('best_position', 0)))
        meta.add_row("Сред. позиция:", f"{stats.get('avg_position', 0):.1f}")

    content.append(meta)

    return Panel(Group(*content), title="Пилот", border_style="cyan", padding=(1, 2))