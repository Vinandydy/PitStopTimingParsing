"""Команды для работы с заездами"""
import typer
from typing import Optional
from rich.console import Console

from ..api_client import APIClient
from ..formatters import format_heats_table, format_heat_details

app = typer.Typer(no_args_is_help=True, help="Управление заездами")
console = Console()


@app.command("list")
def list_heats(
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    session_type: Optional[str] = typer.Option(None, "--type", "-y", help="Тип заезда (Race/Qualification/Practice)"),
    championship: Optional[str] = typer.Option(None, "--champ", "-c", help="Чемпионат"),
    limit: int = typer.Option(20, "--limit", "-l", help="Лимит записей"),
):
    """Показать список заездов"""
    client = APIClient()
    heats = client.get_heats(
        track=track_id,
        session_type=session_type,
        championship=championship
    )

    if limit:
        heats = heats[:limit]

    if not heats:
        console.print("[yellow]Заезды не найдены[/yellow]")
        return

    format_heats_table(heats)
    console.print(f"\n[green]Показано: {len(heats)} заездов[/green]")


@app.command("get")
def get_heat(
    heat_id: int = typer.Argument(..., help="ID заезда"),
):
    """Показать детальную информацию о заезде"""
    client = APIClient()
    heat = client.get_heat(heat_id)

    if not heat:
        console.print(f"[red]Заезд с ID {heat_id} не найден[/red]")
        return

    format_heat_details(heat)


@app.command("latest")
def latest_heats(
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    limit: int = typer.Option(10, "--limit", "-l", help="Количество заездов"),
):
    """Показать последние заезды"""
    client = APIClient()
    heats = client.get_heats(track=track_id)

    if not heats:
        console.print("[yellow]Заезды не найдены[/yellow]")
        return

    # Показываем последние N
    heats = heats[:limit]

    format_heats_table(heats)