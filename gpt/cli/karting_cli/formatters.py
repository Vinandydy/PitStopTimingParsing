"""Форматтеры для вывода данных"""
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
import json
import csv
from io import StringIO

console = Console()


def format_ms_to_time(ms: int) -> str:
    """Конвертирует миллисекунды в читаемый формат"""
    if not ms:
        return "-"
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    milliseconds = ms % 1000
    if minutes > 0:
        return f"{minutes}:{seconds:02d}.{milliseconds:03d}"
    return f"{seconds}.{milliseconds:03d}"


def format_tracks_table(tracks: List[Dict]) -> None:
    """Выводит список треков в виде таблицы"""
    if not tracks:
        console.print("[yellow]Нет данных[/yellow]")
        return

    table = Table(title="🏁 Треки", show_lines=True)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Слаг", style="green")
    table.add_column("Название", style="yellow")

    for track in tracks:
        table.add_row(str(track.get("id", "")), track.get("slug", ""), track.get("name", ""))

    console.print(table)


def format_drivers_table(drivers: List[Dict]) -> None:
    """Выводит список гонщиков в виде таблицы"""
    if not drivers:
        console.print("[yellow]Гонщики не найдены[/yellow]")
        return

    table = Table(title="🏎️ Гонщики", show_lines=True)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("External ID", style="blue", justify="right")
    table.add_column("Имя", style="green")
    table.add_column("Команда", style="yellow")
    table.add_column("Трек", style="magenta")
    table.add_column("Заездов", justify="right")
    table.add_column("Лучший круг", style="cyan")

    for driver in drivers:
        table.add_row(
            str(driver.get("id", "")),
            str(driver.get("external_id", "")),
            driver.get("name", ""),
            driver.get("team", "-"),
            driver.get("track_name", ""),
            str(driver.get("total_races", 0)),
            format_ms_to_time(driver.get("best_lap_ms", 0)),
        )

    console.print(table)


def format_karts_table(karts: List[Dict]) -> None:
    """Выводит список картов в виде таблицы"""
    if not karts:
        console.print("[yellow]Карты не найдены[/yellow]")
        return

    table = Table(title="🏎️ Карты", show_lines=True)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Номер", style="green", justify="right")
    table.add_column("Трек", style="yellow")
    table.add_column("Статус", style="magenta")
    table.add_column("Заездов", justify="right")
    table.add_column("Средний круг", style="cyan")
    table.add_column("Лучший круг", style="cyan")

    for kart in karts:
        status = "🟢 Активен" if kart.get("is_active") else "🔴 Неактивен"
        table.add_row(
            str(kart.get("id", "")),
            str(kart.get("number", "")),
            kart.get("track_name", ""),
            status,
            str(kart.get("total_races", 0)),
            format_ms_to_time(kart.get("avg_lap_ms", 0)),
            format_ms_to_time(kart.get("best_lap_ms", 0)),
        )

    console.print(table)


def format_heats_table(heats: List[Dict]) -> None:
    """Выводит список заездов в виде таблицы"""
    if not heats:
        console.print("[yellow]Заезды не найдены[/yellow]")
        return

    table = Table(title="🏁 Заезды", show_lines=True)
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("External ID", style="blue", justify="right")
    table.add_column("Название", style="green")
    table.add_column("Трек", style="yellow")
    table.add_column("Дата", style="magenta")
    table.add_column("Тип", style="cyan")
    table.add_column("Участников", justify="right")

    for heat in heats:
        scheduled_at = heat.get("scheduled_at", "")
        if scheduled_at:
            scheduled_at = scheduled_at[:19].replace("T", " ")

        table.add_row(
            str(heat.get("id", "")),
            str(heat.get("external_id", "")),
            heat.get("name", "-")[:40],
            heat.get("track_name", ""),
            scheduled_at,
            heat.get("session_type", "-"),
            str(heat.get("participants_count", 0)),
        )

    console.print(table)


def format_heat_details(heat: Dict) -> None:
    """Выводит детальную информацию о заезде"""
    console.print(Panel.fit(
        f"[bold cyan]Заезд #{heat.get('external_id')}[/bold cyan]\n"
        f"[green]{heat.get('name', '-')}[/green]\n\n"
        f"🏁 Трек: [yellow]{heat.get('track_name')}[/yellow]\n"
        f"📅 Дата: [magenta]{heat.get('scheduled_at', '-')[:19].replace('T', ' ')}[/magenta]\n"
        f"🏎️ Тип: [cyan]{heat.get('session_type', '-')}[/cyan]\n"
        f"🏆 Чемпионат: [blue]{heat.get('championship', '-')}[/blue]\n"
        f"🔄 Кругов: [green]{heat.get('laps_count', 0)}[/green]",
        title="📊 Детали заезда"
    ))

    results = heat.get("results", [])
    if not results:
        console.print("[yellow]Нет результатов[/yellow]")
        return

    table = Table(title="📋 Результаты", show_lines=True)
    table.add_column("Поз.", style="cyan", justify="right")
    table.add_column("Гонщик", style="green")
    table.add_column("Карт", style="yellow", justify="right")
    table.add_column("Лучший круг", style="magenta")
    table.add_column("Средний круг", style="blue")
    table.add_column("Круги", justify="right")
    table.add_column("Отставание", style="red")

    for result in results:
        table.add_row(
            str(result.get("position", "")),
            result.get("driver_name", "-"),
            str(result.get("kart_number", "-")),
            format_ms_to_time(result.get("best_lap_ms", 0)),
            format_ms_to_time(result.get("avg_lap_ms", 0)),
            str(result.get("laps_completed", 0)),
            format_ms_to_time(result.get("gap_to_leader_ms", 0)),
        )

    console.print(table)


def format_driver_stats(driver: Dict) -> None:
    """Выводит статистику гонщика"""
    console.print(Panel.fit(
        f"[bold cyan]🏎️ {driver.get('name')}[/bold cyan]\n"
        f"🏁 Трек: [yellow]{driver.get('track_name')}[/yellow]\n"
        f"👥 Команда: [green]{driver.get('team', '-')}[/green]\n\n"
        f"📊 Статистика:\n"
        f"  • Всего заездов: [bold]{driver.get('total_races', 0)}[/bold]\n"
        f"  • Лучший круг: [cyan]{format_ms_to_time(driver.get('best_lap_ms', 0))}[/cyan]\n"
        f"  • Средний круг: [blue]{format_ms_to_time(driver.get('avg_lap_ms', 0))}[/blue]",
        title="📊 Статистика гонщика"
    ))


def format_kart_stats(kart: Dict) -> None:
    """Выводит статистику карта"""
    console.print(Panel.fit(
        f"[bold cyan]🏎️ Карт #{kart.get('number')}[/bold cyan]\n"
        f"🏁 Трек: [yellow]{kart.get('track_name')}[/yellow]\n"
        f"🟢 Статус: [green]{'Активен' if kart.get('is_active') else 'Неактивен'}[/green]\n\n"
        f"📊 Статистика:\n"
        f"  • Всего заездов: [bold]{kart.get('total_races', 0)}[/bold]\n"
        f"  • Лучший круг: [cyan]{format_ms_to_time(kart.get('best_lap_ms', 0))}[/cyan]\n"
        f"  • Средний круг: [blue]{format_ms_to_time(kart.get('avg_lap_ms', 0))}[/blue]",
        title="📊 Статистика карта"
    ))


def format_export(data: List[Dict], format_type: str) -> str:
    """Форматирует данные для экспорта"""
    if not data:
        return ""

    if format_type == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)

    if format_type == "csv":
        output = StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return output.getvalue()

    return str(data)


def show_progress() -> Progress:
    """Показывает индикатор прогресса"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )