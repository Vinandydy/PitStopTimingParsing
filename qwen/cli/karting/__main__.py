"""Точка входа: python -m karting"""

import sys

import typer
from rich.console import Console

from qwen.cli.karting import __version__
from qwen.cli.karting.commands import ai, drivers, export, heats, results, stats, tracks
from qwen.cli.karting.config import get_config
from qwen.cli.karting.exceptions import CLIError

# Инициализация Typer
app = typer.Typer(
    name="karting",
    help="🏁 CLI для анализа статистики timing.batyrshin.name",
    no_args_is_help=True,
    add_completion=True,
)

# Регистрация команд (7 штук)
app.add_typer(heats.app, name="heats", help="🏁 Работа с заездами")
app.add_typer(drivers.app, name="drivers", help="👤 Пилоты")
app.add_typer(results.app, name="results", help="📊 Результаты заездов")
app.add_typer(stats.app, name="stats", help="📈 Статистика и аналитика")
app.add_typer(export.app, name="export", help="💾 Экспорт данных")
app.add_typer(tracks.app, name="tracks", help="🗺️ Треки")
app.add_typer(ai.app, name="ai", help="🤖 AI-анализ")


# Глобальные опции
@app.callback()
def main(
        version: bool = typer.Option(False, "--version", "-V", help="Версия CLI", is_eager=True),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Подробный вывод", envvar="KARTING_VERBOSE"),
        api_url: str = typer.Option(None, "--api-url", help="URL вашего API", envvar="KARTING_API_URL"),
):
    if version:
        Console().print(f"karting v{__version__}")
        raise typer.Exit()

    # Применяем api_url из CLI, если передан
    if api_url:
        cfg = get_config()
        cfg.api_base_url = api_url.rstrip('/')


# Обработчик ошибок
def run():
    try:
        app()
    except CLIError as e:
        e.display()
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        Console(stderr=True).print("\n[yellow]⚠️  Прервано[/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    run()