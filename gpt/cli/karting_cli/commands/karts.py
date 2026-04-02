"""Команды для работы с картами"""
import typer
from typing import Optional
from rich.console import Console

from ..api_client import APIClient
from ..formatters import format_karts_table, format_kart_stats

app = typer.Typer(no_args_is_help=True, help="Управление картами")
console = Console()


@app.command("list")
def list_karts(
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    active_only: bool = typer.Option(False, "--active", "-a", help="Только активные"),
    limit: int = typer.Option(20, "--limit", "-l", help="Лимит записей"),
):
    """Показать список картов"""
    client = APIClient()
    karts = client.get_karts(track=track_id, is_active=active_only or None)

    if limit:
        karts = karts[:limit]

    if not karts:
        console.print("[yellow]Карты не найдены[/yellow]")
        return

    format_karts_table(karts)
    console.print(f"\n[green]Показано: {len(karts)} картов[/green]")


@app.command("get")
def get_kart(
    kart_id: int = typer.Argument(..., help="ID карта"),
):
    """Показать информацию о карте"""
    client = APIClient()
    kart = client.get_kart(kart_id)

    if not kart:
        console.print(f"[red]Карт с ID {kart_id} не найден[/red]")
        return

    format_kart_stats(kart)


@app.command("stats")
def kart_stats(
    kart_id: int = typer.Argument(..., help="ID карта"),
    period: str = typer.Option("all", "--period", "-p", help="Период (all, 7d, 30d)"),
):
    """Показать статистику карта"""
    client = APIClient()
    kart = client.get_kart(kart_id)

    if not kart:
        console.print(f"[red]Карт с ID {kart_id} не найден[/red]")
        return

    format_kart_stats(kart)


@app.command("active")
def active_karts(
    track_id: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
):
    """Показать активные карты"""
    client = APIClient()
    karts = client.get_karts(track=track_id, is_active=True)

    if not karts:
        console.print("[yellow]Активные карты не найдены[/yellow]")
        return

    format_karts_table(karts)
    console.print(f"\n[green]Всего активных: {len(karts)}[/green]")