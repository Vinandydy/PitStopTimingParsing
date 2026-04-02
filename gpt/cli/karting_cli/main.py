"""Главный entry point CLI утилиты"""
import typer
from rich.console import Console
from typing import Optional

from .commands import drivers, karts, heats, tracks, stats, parser, export
from .config import Config

console = Console()

app = typer.Typer(
    name="timing-cli",
    help="CLI утилита для работы с данными timing.batyrshin.name",
    add_completion=False,
    no_args_is_help=True,
)

# Подключаем команды
app.add_typer(tracks.app, name="tracks", help="Управление треками")
app.add_typer(drivers.app, name="drivers", help="Управление гонщиками")
app.add_typer(karts.app, name="karts", help="Управление картами")
app.add_typer(heats.app, name="heats", help="Управление заездами")
app.add_typer(stats.app, name="stats", help="Статистика")
app.add_typer(parser.app, name="parser", help="Управление парсером")
app.add_typer(export.app, name="export", help="Экспорт данных")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Показать текущую конфигурацию"),
    set_api: Optional[str] = typer.Option(None, "--set-api", help="Установить URL API"),
    set_verbose: Optional[bool] = typer.Option(None, "--set-verbose", help="Включить/выключить verbose режим"),
    reset: bool = typer.Option(False, "--reset", "-r", help="Сбросить конфигурацию"),
):
    """Управление настройками CLI"""
    cfg = Config()

    if reset:
        cfg.reset()
        console.print("[green]✅ Конфигурация сброшена к значениям по умолчанию[/green]")
        return

    if show:
        console.print("\n[bold cyan]📁 Текущая конфигурация:[/bold cyan]")
        console.print(f"  • API URL: [yellow]{cfg.get('api_url')}[/yellow]")
        console.print(f"  • Таймаут: [yellow]{cfg.get('timeout')} сек[/yellow]")
        console.print(f"  • Verbose: [yellow]{cfg.get('verbose')}[/yellow]")
        console.print(f"  • Page Size: [yellow]{cfg.get('page_size')}[/yellow]")
        console.print(f"  • Конфиг файл: [dim]{cfg.CONFIG_FILE}[/dim]")
        return

    if set_api:
        cfg.set("api_url", set_api)
        console.print(f"[green]✅ API URL установлен: {set_api}[/green]")

    if set_verbose is not None:
        cfg.set("verbose", set_verbose)
        console.print(f"[green]✅ Verbose режим: {'включен' if set_verbose else 'выключен'}[/green]")


@app.command()
def version():
    """Показать версию утилиты"""
    from . import __version__
    console.print(f"[bold cyan]Timing CLI (GPT)[/bold cyan] version [yellow]{__version__}[/yellow]")


if __name__ == "__main__":
    app()