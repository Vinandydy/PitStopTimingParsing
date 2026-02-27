"""Команды для работы с треками (Track)."""

import json

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from karting.client import APIClient
from karting.config import get_config

app = typer.Typer(help="🗺️ Треки")
console = Console()

@app.command("list")
def list_tracks(
    search: str | None = typer.Option(None, "--search", "-s", help="Поиск по названию"),
    limit: int = typer.Option(50, "--limit", "-l", help="Максимальное количество записей (1-200)"),
    format: str = typer.Option(None, "--format", "-F", case_sensitive=False, help="Формат вывода"),
):
    """📋 Список треков"""

    # Валидация limit
    if limit < 1:
        raise typer.BadParameter("limit должен быть >= 1", param_hint="--limit")
    if limit > 200:
        raise typer.BadParameter("limit должен быть <= 200", param_hint="--limit")

    cfg = get_config()
    out_fmt = format or cfg.default_format

    params = {'limit': limit}
    if search:
        params['search'] = search

    with console.status("[bold green]Загрузка...[/bold green]"), APIClient() as api:
        resp = api.list_tracks(**params)

    tracks = resp.get('results', [resp]) if 'results' in resp else [resp]

    if out_fmt == "json":
        console.print(JSON(json.dumps(tracks, ensure_ascii=False, indent=2)))
    else:
        if not tracks:
            console.print("[yellow]⚠️  Ничего не найдено[/yellow]")
            return

        table = Table(title=f"🗺️ Треки ({len(tracks)})", show_lines=True)
        table.add_column("ID", style="dim", width=6)
        table.add_column("Slug", style="cyan")
        table.add_column("Название", style="bold")

        for t in tracks:
            table.add_row(str(t['id']), t.get('slug', '—'), t.get('name', '—'))

        console.print(table)