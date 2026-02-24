"""Команды для работы с пилотами (Driver)."""

import json
from typing import Optional
import typer
from rich.console import Console
from rich.json import JSON

from karting.client import APIClient
from karting.config import get_config
from karting.exceptions import APIResourceNotFound, CLIError
from karting.formatters.tables import render_drivers_table
from karting.formatters.cards import render_driver_card

app = typer.Typer(help="👤 Пилоты")
console = Console()

@app.command("list")
def list_drivers(
    track: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    team: Optional[str] = typer.Option(None, "--team", "-T", help="Команда"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Поиск по имени"),
    limit: int = typer.Option(50, "--limit", "-l", help="Максимальное количество записей (1-200)"),
    format: str = typer.Option(None, "--format", "-F", case_sensitive=False, help="Формат вывода"),
):
    """📋 Список пилотов"""

    # Валидация limit
    if limit < 1:
        raise typer.BadParameter("limit должен быть >= 1", param_hint="--limit")
    if limit > 200:
        raise typer.BadParameter("limit должен быть <= 200", param_hint="--limit")

    cfg = get_config()
    out_fmt = format or cfg.default_format

    params = {'limit': limit}
    if track:
        params['track'] = track
    if team:
        params['team'] = team
    if search:
        params['search'] = search

    with console.status("[bold green]Загрузка...[/bold green]"):
        with APIClient() as api:
            resp = api.list_drivers(**params)

    drivers = resp.get('results', [resp]) if 'results' in resp else [resp]

    if out_fmt == "json":
        console.print(JSON(json.dumps(drivers, ensure_ascii=False, indent=2)))
    else:
        if not drivers:
            console.print("[yellow]⚠️  Ничего не найдено[/yellow]")
            return
        console.print(render_drivers_table(drivers, title=f"👤 Пилоты ({len(drivers)})"))

@app.command("detail")
def driver_detail(
    driver_id: int = typer.Argument(..., help="ID пилота"),
    format: str = typer.Option(None, "--format", "-F", case_sensitive=False, help="Формат вывода"),
):
    """🔍 Детали пилота"""
    cfg = get_config()
    out_fmt = format or cfg.default_format

    with console.status(f"[bold green]Загрузка #{driver_id}...[/bold green]"):
        with APIClient() as api:
            try:
                driver = api.get_driver(driver_id)
            except APIResourceNotFound:
                console.print(f"[bold red]❌ Пилот #{driver_id} не найден[/bold red]")
                raise typer.Exit(5)

    if out_fmt == "json":
        console.print(JSON(json.dumps(driver, ensure_ascii=False, indent=2)))
    else:
        console.print(render_driver_card(driver))