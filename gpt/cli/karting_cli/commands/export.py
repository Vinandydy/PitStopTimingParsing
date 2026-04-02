"""Команды для экспорта данных"""
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console

from ..api_client import APIClient
from ..formatters import format_export

app = typer.Typer(no_args_is_help=True, help="Экспорт данных")
console = Console()


@app.command("drivers")
def export_drivers(
    format: str = typer.Option("json", "--format", "-f", help="Формат (json, csv)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Файл для сохранения"),
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
):
    """Экспортировать гонщиков"""
    client = APIClient()
    drivers = client.get_drivers(track=track_id)

    if not drivers:
        console.print("[yellow]Нет данных для экспорта[/yellow]")
        return

    data = format_export(drivers, format)

    if output:
        output.write_text(data, encoding="utf-8")
        console.print(f"[green]✅ Данные сохранены в {output}[/green]")
    else:
        console.print(data)


@app.command("karts")
def export_karts(
    format: str = typer.Option("json", "--format", "-f", help="Формат (json, csv)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Файл для сохранения"),
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    active_only: bool = typer.Option(False, "--active", "-a", help="Только активные"),
):
    """Экспортировать карты"""
    client = APIClient()
    karts = client.get_karts(track=track_id, is_active=active_only or None)

    if not karts:
        console.print("[yellow]Нет данных для экспорта[/yellow]")
        return

    data = format_export(karts, format)

    if output:
        output.write_text(data, encoding="utf-8")
        console.print(f"[green]✅ Данные сохранены в {output}[/green]")
    else:
        console.print(data)


@app.command("heats")
def export_heats(
    format: str = typer.Option("json", "--format", "-f", help="Формат (json, csv)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Файл для сохранения"),
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    limit: int = typer.Option(100, "--limit", "-l", help="Лимит записей"),
):
    """Экспортировать заезды"""
    client = APIClient()
    heats = client.get_heats(track=track_id)

    if limit:
        heats = heats[:limit]

    if not heats:
        console.print("[yellow]Нет данных для экспорта[/yellow]")
        return

    data = format_export(heats, format)

    if output:
        output.write_text(data, encoding="utf-8")
        console.print(f"[green]✅ Данные сохранены в {output}[/green]")
    else:
        console.print(data)