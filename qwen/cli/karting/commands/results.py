"""Команды для работы с результатами (HeatParticipation)."""

import json

import typer
from rich.console import Console
from rich.json import JSON

from qwen.cli.karting.client import APIClient
from qwen.cli.karting.config import get_config
from qwen.cli.karting.formatters.tables import render_results_table

app = typer.Typer(help="📊 Результаты заездов")
console = Console()

@app.command("list")
def list_results(
    heat: int | None = typer.Option(None, "--heat", "-H", help="ID заезда"),
    driver: int | None = typer.Option(None, "--driver", "-D", help="ID пилота"),
    kart: int | None = typer.Option(None, "--kart", "-K", help="ID карта"),
    position: int | None = typer.Option(None, "--position", "-p", help="Позиция"),
    limit: int = typer.Option(50, "--limit", "-l", help="Максимальное количество записей (1-200)"),
    format: str = typer.Option(None, "--format", "-F", case_sensitive=False, help="Формат вывода"),
):
    """📋 Список результатов"""

    # Валидация limit
    if limit < 1:
        raise typer.BadParameter("limit должен быть >= 1", param_hint="--limit")
    if limit > 200:
        raise typer.BadParameter("limit должен быть <= 200", param_hint="--limit")

    cfg = get_config()
    out_fmt = format or cfg.default_format

    params = {'limit': limit, 'ordering': 'position'}
    if heat:
        params['heat'] = heat
    if driver:
        params['driver'] = driver
    if kart:
        params['kart'] = kart
    if position:
        params['position'] = position

    with console.status("[bold green]Загрузка...[/bold green]"), APIClient() as api:
        resp = api.list_results(**params)

    results = resp.get('results', [resp]) if 'results' in resp else [resp]

    if out_fmt == "json":
        console.print(JSON(json.dumps(results, ensure_ascii=False, indent=2)))
    else:
        if not results:
            console.print("[yellow]⚠️  Ничего не найдено[/yellow]")
            return
        console.print(render_results_table(results, title=f"📊 Результаты ({len(results)})"))