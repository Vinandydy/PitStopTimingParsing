"""Команды экспорта данных."""

import csv
import json

import typer
from rich.console import Console

from qwen.cli.karting.client import APIClient

app = typer.Typer(help="💾 Экспорт данных")
console = Console()


@app.command("csv")
def export_csv(
        heat: int | None = typer.Option(None, "--heat", "-H", help="ID заезда"),
        driver: int | None = typer.Option(None, "--driver", "-D", help="ID пилота"),
        output: str = typer.Option("export.csv", "--output", "-o", help="Файл для экспорта"),
):
    """💾 Экспорт в CSV"""
    params = {'limit': 500}
    if heat:
        params['heat'] = heat
    if driver:
        params['driver'] = driver

    with console.status("[bold green]Загрузка данных...[/bold green]"), APIClient() as api:
        resp = api.list_results(**params)

    results = resp.get('results', [resp]) if 'results' in resp else [resp]

    if not results:
        console.print("[yellow]⚠️  Нет данных для экспорта[/yellow]")
        return

    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['position', 'driver_name', 'kart_number', 'best_lap_formatted',
                                               'avg_lap_formatted', 'laps_completed'])
        writer.writeheader()
        for r in results:
            writer.writerow({
                'position': r.get('position', ''),
                'driver_name': r.get('driver_name', ''),
                'kart_number': r.get('kart_number', ''),
                'best_lap_formatted': r.get('best_lap_formatted', ''),
                'avg_lap_formatted': r.get('avg_lap_formatted', ''),
                'laps_completed': r.get('laps_completed', ''),
            })

    console.print(f"[bold green]✓[/bold green] Экспортировано {len(results)} записей в {output}")


@app.command("json")
def export_json(
        heat: int | None = typer.Option(None, "--heat", "-H"),
        driver: int | None = typer.Option(None, "--driver", "-D"),
        output: str = typer.Option("export.json", "--output", "-o", help="Файл для экспорта"),
):
    """💾 Экспорт в JSON"""
    params = {'limit': 500}
    if heat:
        params['heat'] = heat
    if driver:
        params['driver'] = driver

    with console.status("[bold green]Загрузка данных...[/bold green]"), APIClient() as api:
        resp = api.list_results(**params)

    results = resp.get('results', [resp]) if 'results' in resp else [resp]

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    console.print(f"[bold green]✓[/bold green] Экспортировано {len(results)} записей в {output}")