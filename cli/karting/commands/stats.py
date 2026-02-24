"""Команды статистики и аналитики."""

import json
from typing import Optional
import typer
from rich.console import Console
from rich.json import JSON

from karting.client import APIClient
from karting.config import get_config
from karting.exceptions import CLIError
from karting.formatters.cards import render_driver_card

app = typer.Typer(help="📈 Статистика и аналитика")
console = Console()


@app.command("driver")
def driver_stats(
        driver_id: int = typer.Argument(..., help="ID пилота"),
        period: str = typer.Option("all", "--period", "-p", case_sensitive=False),
        format: str = typer.Option(None, "--format", "-F", case_sensitive=False),
):
    """📊 Статистика пилота"""
    cfg = get_config()
    out_fmt = format or cfg.default_format

    with console.status(f"[bold green]Загрузка статистики #{driver_id}...[/bold green]"):
        with APIClient() as api:
            driver = api.get_driver(driver_id)
            results = api.list_results(driver=driver_id, limit=50, ordering='-heat__scheduled_at')

    stats = {
        'total_races': len(results.get('results', [])),
        'best_position': min((r['position'] for r in results.get('results', []) if r['position']), default=0),
        'avg_position': sum(r['position'] for r in results.get('results', [])) / max(len(results.get('results', [])),
                                                                                     1),
    }

    if out_fmt == "json":
        console.print(JSON(json.dumps({'driver': driver, 'stats': stats}, ensure_ascii=False, indent=2)))
    else:
        console.print(render_driver_card(driver, stats))