"""Команды для управления парсером"""
import typer
from rich.console import Console
from rich.panel import Panel

from ..api_client import APIClient

app = typer.Typer(no_args_is_help=True, help="Управление парсером")
console = Console()


@app.command("run")
def run_parser(
    parser_type: str = typer.Argument(
        "heats",
        help="Тип парсинга (heats, karts, drivers, all)"
    ),
    track: str = typer.Option("premium", "--track", "-t", help="Слаг трека"),
):
    """Запустить парсер"""
    client = APIClient()

    console.print(Panel.fit(
        f"🚀 Запуск парсера\n"
        f"📦 Тип: [cyan]{parser_type}[/cyan]\n"
        f"🏁 Трек: [yellow]{track}[/yellow]",
        title="Parser"
    ))

    result = client.run_parser(parser_type, track)

    if result:
        console.print("\n[green]✅ Парсер успешно запущен[/green]")
        if result.get("task_id"):
            console.print(f"📋 ID задачи: {result['task_id']}")
    else:
        console.print("\n[red]❌ Ошибка при запуске парсера[/red]")


@app.command("status")
def parser_status():
    """Показать статус парсера"""
    console.print("[yellow]ℹ️ Функция в разработке[/yellow]")
    console.print("Статус парсера будет доступен в следующей версии")