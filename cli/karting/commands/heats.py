"""Команды для работы с заездами (Heat)."""

import json
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.json import JSON

from karting.client import APIClient
from karting.config import get_config
from karting.exceptions import APIResourceNotFound, CLIError
from karting.formatters.tables import render_heats_table, render_results_table
from karting.formatters.cards import render_heat_card
from karting.utils import format_date, ms_to_formatted, session_icon

app = typer.Typer(help="🏁 Работа с заездами")
console = Console()

@app.command("list")
def list_heats(
    track: Optional[int] = typer.Option(None, "--track", "-t", help="ID трека"),
    session_type: Optional[str] = typer.Option(None, "--type", "-T", case_sensitive=False, help="Тип сессии"),
    championship: Optional[str] = typer.Option(None, "--champ", "-c", help="Чемпионат"),
    date_from: Optional[str] = typer.Option(None, "--from", "-f", help="Дата от (YYYY-MM-DD)"),
    date_to: Optional[str] = typer.Option(None, "--to", "-d", help="Дата до (YYYY-MM-DD)"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Поиск"),
    limit: int = typer.Option(50, "--limit", "-l", help="Максимальное количество записей (1-200)"),
    format: str = typer.Option(None, "--format", "-F", case_sensitive=False, help="Формат вывода"),
):
    """📋 Список заездов (использует HeatFilter)"""

    # Валидация limit
    if limit < 1:
        raise typer.BadParameter("limit должен быть >= 1", param_hint="--limit")
    if limit > 200:
        raise typer.BadParameter("limit должен быть <= 200", param_hint="--limit")

    cfg = get_config()
    out_fmt = format or cfg.default_format

    params = {'limit': limit, 'ordering': '-scheduled_at'}
    if track:
        params['track'] = track
    if session_type:
        params['session_type'] = session_type
    if championship:
        params['championship'] = championship
    if date_from:
        params['scheduled_at_from'] = date_from
    if date_to:
        params['scheduled_at_to'] = date_to
    if search:
        params['search'] = search

    with console.status("[bold green]Загрузка...[/bold green]"):
        with APIClient() as api:
            resp = api.list_heats(**params)

    heats = resp.get('results', [resp]) if 'results' in resp else [resp]

    if out_fmt == "json":
        console.print(JSON(json.dumps(heats, ensure_ascii=False, indent=2)))
    else:
        if not heats:
            console.print("[yellow]⚠️  Ничего не найдено[/yellow]")
            return
        console.print(render_heats_table(heats, title=f"🏁 Заезды ({len(heats)})"))

@app.command("detail")
def heat_detail(
        heat_id: int = typer.Argument(..., help="ID заезда"),
        format: str = typer.Option(None, "--format", "-F", case_sensitive=False, help="Формат вывода"),
):
    """🔍 Детали заезда + результаты"""

    cfg = get_config()
    out_fmt = format or cfg.default_format

    with console.status(f"[bold green]Загрузка #{heat_id}...[/bold green]"):
        with APIClient() as api:
            try:
                heat = api.get_heat(heat_id)
            except APIResourceNotFound:
                console.print(f"[bold red]❌ Заезд #{heat_id} не найден[/bold red]")
                # Подсказка: показать доступные ID
                try:
                    recent = api.list_heats(limit=5)
                    ids = [str(h['id']) for h in recent.get('results', recent)[:5]]
                    console.print(f"[dim]💡 Доступные ID: {', '.join(ids)}[/dim]")
                except:
                    pass
                raise typer.Exit(5)

    if out_fmt == "json":
        console.print(JSON(json.dumps(heat, ensure_ascii=False, indent=2)))
        return

    # === Форматированный вывод (таблица + результаты) ===

    # 1. Заголовок заезда
    header = Table.grid(padding=(0, 1))
    header.add_column(style="bold green")
    header.add_column(style="dim")

    header.add_row(
        f"🏁 {heat.get('name', 'Без названия')}",
        f"ID: {heat.get('id')} | External: {heat.get('external_id', '—')}"
    )
    header.add_row(
        f"{heat.get('track_name', '—')} • {format_date(heat.get('scheduled_at', ''), short=True)}",
        f"{session_icon(heat.get('session_type'))} {heat.get('session_type', 'Race')} | 🏆 {heat.get('championship', '—')}"
    )

    console.print(header)
    console.print()

    # 2. Мета-информация
    meta = Table.grid(padding=(0, 2))
    meta.add_column(style="dim", width=15)
    meta.add_column()

    meta.add_row("План кругов:", str(heat.get('laps_count', '—')))
    meta.add_row("Участников:", str(len(heat.get('results', []))))

    console.print(meta)
    console.print()

    # 3. Результаты (если есть)
    results = heat.get('results', [])
    if results:
        console.print("📊 Результаты:")
        console.print(render_results_table(results[:10]))  # Топ-10

        if len(results) > 10:
            console.print(f"[dim]... ещё {len(results) - 10} результатов[/dim]")
    else:
        console.print("[yellow]⚠️  Результаты ещё не загружены[/yellow]")