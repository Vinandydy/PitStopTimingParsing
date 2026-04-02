"""Команды для работы с треками"""
import typer
from rich.console import Console

from ..api_client import APIClient
from ..formatters import format_tracks_table

app = typer.Typer(no_args_is_help=True, help="Управление треками")
console = Console()


@app.command("list")
def list_tracks():
    """Показать список треков"""
    client = APIClient()
    tracks = client.get_tracks()

    if not tracks:
        console.print("[yellow]Треки не найдены[/yellow]")
        return

    format_tracks_table(tracks)
    console.print(f"\n[green]Всего: {len(tracks)} треков[/green]")