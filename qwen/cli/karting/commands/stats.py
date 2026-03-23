# cli/karting/commands/stats.py

import json

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from qwen.cli.karting.client import APIClient
from qwen.cli.karting.config import get_config
from qwen.cli.karting.exceptions import APIResourceNotFound

app = typer.Typer(help="📈 Статистика и аналитика")
console = Console()

@app.command("driver")
def driver_stats(
    driver_id: int = typer.Argument(..., help="ID пилота"),
    period: str = typer.Option("all", "--period", "-p",
                               help="Период: all, 7d, 30d, 90d",
                               case_sensitive=False),
    format: str = typer.Option(None, "--format", "-F",
                               case_sensitive=False, help="Формат вывода"),
):
    """📊 Статистика пилота с расчётом метрик"""

    cfg = get_config()
    out_fmt = format or cfg.default_format

    with console.status("[bold green]Загрузка данных пилота...[/bold green]"):
        with APIClient() as api:
            try:
                # 1. Получаем базовую инфо о пилоте
                driver = api.get_driver(driver_id)

                # 2. Получаем результаты пилота за период
                params = {'driver': driver_id, 'limit': 500, 'ordering': '-heat__scheduled_at'}
                results_resp = api.list_results(**params)
                results = results_resp.get('results', [results_resp]) if 'results' in results_resp else [results_resp]

            except APIResourceNotFound:
                console.print(f"[bold red]❌ Пилот #{driver_id} не найден[/bold red]")
                raise typer.Exit(5)

    # 3. Вычисляем статистику из результатов
    stats = _calculate_driver_stats(results)

    # 4. Формируем вывод
    if out_fmt == "json":
        console.print(JSON(json.dumps({
            'driver': driver,
            'stats': stats,
            'total_results': len(results)
        }, ensure_ascii=False, indent=2)))
    else:
        # Карточка пилота с исправленными данными
        console.print(_render_driver_stats_card(driver, stats))

        # Таблица последних заездов
        if results:
            console.print("\n📊 Последние 10 заездов:")
            console.print(_render_recent_results_table(results[:10]))

def _calculate_driver_stats(results: list) -> dict:
    """Вычисляет статистику пилота из результатов."""

    if not results:
        return {
            'total_races': 0,
            'best_position': None,
            'avg_position': 0,
            'best_lap_ms': 0,
            'best_lap_formatted': '—',
            'total_points': 0,
            'wins': 0,
            'podiums': 0,
        }

    # Фильтруем валидные результаты
    valid_results = [r for r in results if r.get('position', 0) > 0]

    positions = [r['position'] for r in valid_results]
    best_laps = [r.get('best_lap_ms', 0) for r in valid_results if r.get('best_lap_ms', 0) > 0]

    # Подсчёт очков (примерная система: 1 место=25, 2=18, 3=15, 4=12, 5=10, 6=8, 7=6, 8=4, 9=2, 10=1)
    points_map = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}
    total_points = sum(points_map.get(r['position'], 0) for r in valid_results)

    return {
        'total_races': len(valid_results),
        'best_position': min(positions) if positions else None,
        'avg_position': sum(positions) / len(positions) if positions else 0,
        'best_lap_ms': min(best_laps) if best_laps else 0,
        'best_lap_formatted': _format_ms(min(best_laps)) if best_laps else '—',
        'total_points': total_points,
        'wins': sum(1 for p in positions if p == 1),
        'podiums': sum(1 for p in positions if p <= 3),
    }

def _format_ms(ms: int) -> str:
    """Форматирует миллисекунды в MM:SS.mmm"""
    if not ms or ms <= 0:
        return '—'
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    return f"{minutes}:{seconds:02d}.{milliseconds:03d}" if minutes else f"{seconds}.{milliseconds:03d}"

def _render_driver_stats_card(driver: dict, stats: dict) -> Panel:
    """Рендерит карточку пилота со статистикой."""
    from rich.console import Group
    from rich.table import Table

    content = []

    # Заголовок
    header = Text.assemble(
        ("👤 ", "bold"),
        (driver.get('name', '—'), "bold green"),
    )
    content.append(header)
    content.append("")

    # Основная инфо
    meta = Table.grid(padding=(0, 2))
    meta.add_column(style="dim", width=15)
    meta.add_column()

    meta.add_row("ID:", str(driver.get('id', '—')))
    meta.add_row("Команда:", driver.get('team', '—') or '—')  # ← Исправлено: берём team, не track
    meta.add_row("Всего заездов:", str(stats.get('total_races', 0)))
    meta.add_row("Лучшая позиция:", f"🏆 {stats['best_position']}" if stats.get('best_position') else '—')
    meta.add_row("Сред. позиция:", f"{stats.get('avg_position', 0):.1f}")
    meta.add_row("Побед:", str(stats.get('wins', 0)))
    meta.add_row("Подиумов:", str(stats.get('podiums', 0)))
    meta.add_row("Очков:", str(stats.get('total_points', 0)))
    meta.add_row("Лучший круг:", stats.get('best_lap_formatted', '—'))

    content.append(meta)

    return Panel(
        Group(*content),
        title="📊 Статистика пилота",
        border_style="cyan",
        padding=(1, 2),
        width=min(console.width, 80),
    )

def _render_recent_results_table(results: list) -> Table:
    """Таблица последних результатов."""
    from karting.formatters.tables import render_results_table
    return render_results_table(results, title="Последние заезды")