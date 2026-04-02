"""Команды для статистики"""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from ..api_client import APIClient
from ..formatters import format_ms_to_time

app = typer.Typer(no_args_is_help=True, help="Статистика")
console = Console()


@app.command("summary")
def summary(
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
):
    """Показать общую статистику"""
    client = APIClient()

    # Получаем данные
    tracks = client.get_tracks()
    drivers = client.get_drivers(track=track_id)
    karts = client.get_karts(track=track_id)
    heats = client.get_heats(track=track_id)

    # Вычисляем статистику
    total_heats = len(heats)
    total_drivers = len(drivers)
    total_karts = len(karts)
    active_karts = len([k for k in karts if k.get("is_active")])

    # Лучшие времена
    best_lap_driver = None
    best_lap_time = float("inf")
    for driver in drivers:
        if driver.get("best_lap_ms", 0) and driver.get("best_lap_ms", 0) < best_lap_time:
            best_lap_time = driver.get("best_lap_ms")
            best_lap_driver = driver

    # Таблица статистики
    table = Table(title="📊 Общая статистика", show_lines=True)
    table.add_column("Показатель", style="cyan")
    table.add_column("Значение", style="green")

    table.add_row("Всего заездов", str(total_heats))
    table.add_row("Всего гонщиков", str(total_drivers))
    table.add_row("Всего картов", str(total_karts))
    table.add_row("Активных картов", str(active_karts))

    if best_lap_driver:
        table.add_row(
            "Лучший круг",
            f"{format_ms_to_time(best_lap_time)} ({best_lap_driver.get('name')})"
        )

    console.print(table)