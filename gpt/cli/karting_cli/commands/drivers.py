"""Команды для работы с гонщиками"""
import typer
from typing import Optional
from rich.console import Console

from ..api_client import APIClient
from ..formatters import format_drivers_table, format_driver_stats

app = typer.Typer(no_args_is_help=True, help="Управление гонщиками")
console = Console()


@app.command("list")
def list_drivers(
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Поиск по имени"),
    limit: int = typer.Option(20, "--limit", "-l", help="Лимит записей"),
):
    """Показать список гонщиков"""
    client = APIClient()
    drivers = client.get_drivers(track=track_id, search=search)

    if limit:
        drivers = drivers[:limit]

    if not drivers:
        console.print("[yellow]Гонщики не найдены[/yellow]")
        return

    format_drivers_table(drivers)
    console.print(f"\n[green]Показано: {len(drivers)} гонщиков[/green]")


@app.command("get")
def get_driver(
    driver_id: int = typer.Argument(..., help="ID гонщика"),
):
    """Показать информацию о гонщике"""
    client = APIClient()
    driver = client.get_driver(driver_id)

    if not driver:
        console.print(f"[red]Гонщик с ID {driver_id} не найден[/red]")
        return

    format_driver_stats(driver)


@app.command("stats")
def driver_stats(
    driver_id: int = typer.Argument(..., help="ID гонщика"),
):
    """Показать статистику гонщика"""
    client = APIClient()
    driver = client.get_driver(driver_id)

    if not driver:
        console.print(f"[red]Гонщик с ID {driver_id} не найден[/red]")
        return

    format_driver_stats(driver)


@app.command("top")
def top_drivers(
    limit: int = typer.Option(10, "--limit", "-l", help="Количество в топе"),
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
):
    """Показать топ гонщиков по количеству заездов"""
    client = APIClient()
    drivers = client.get_drivers(track=track_id)

    # Сортируем по заездам
    drivers.sort(key=lambda x: x.get("total_races", 0), reverse=True)
    drivers = drivers[:limit]

    if not drivers:
        console.print("[yellow]Нет данных[/yellow]")
        return

    format_drivers_table(drivers)