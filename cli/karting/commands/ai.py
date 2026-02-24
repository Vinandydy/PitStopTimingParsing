"""AI-команды для анализа данных."""

import json
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from karting.client import APIClient
from karting.config import get_config
from karting.exceptions import CLIError

app = typer.Typer(help="🤖 AI-анализ")
console = Console()


@app.command("insight")
def ai_insight(
        heat_id: Optional[int] = typer.Option(None, "--heat", "-H"),
        driver_id: Optional[int] = typer.Option(None, "--driver", "-D"),
        prompt: Optional[str] = typer.Option(None, "--prompt", "-p"),
        model: str = typer.Option("qwen-cloud", "--model", "-m", case_sensitive=False),
):
    """🔍 AI-инсайт по заезду или пилоту"""
    if not heat_id and not driver_id:
        console.print("[bold red]❌ Укажите --heat ИЛИ --driver[/bold red]")
        raise typer.Exit(2)

    with APIClient() as api:
        if heat_id:
            ctx = api.get_heat(heat_id)
            default_prompt = "Проанализируй заезд: кто показал лучший прогресс? Дай 2 совета пилотам топ-5. Отвечай кратко, на русском."
            label = f"Заезд #{heat_id}: {ctx.get('name', '')}"
        else:
            driver = api.get_driver(driver_id)
            results = api.list_results(driver=driver_id, limit=20, ordering='-heat__scheduled_at')
            ctx = {'driver': driver, 'recent_results': results.get('results', [])}
            default_prompt = f"Тренер для {driver.get('name')}: оцени тренд за последние заезды, дай 3 конкретных совета."
            label = f"Пилот #{driver_id}: {driver.get('name', '')}"

    payload = {
        'prompt': prompt or default_prompt,
        'context': ctx,
        'model': model,
        'temperature': 0.2,
        'max_tokens': 512,
    }

    console.print(f"\n[bold cyan]🔍 Анализирую:[/bold cyan] {label}")

    with console.status("[bold green]🤔 Генерация...[/bold green]"):
        try:
            with APIClient() as api:
                resp = api.request("POST", "/ai/generate/", json_data=payload, use_cache=False)
                insight = resp.get('insight') or resp.get('text', 'Нет ответа')
                console.print("\n" + Panel(Markdown(insight), title="💡 AI-инсайт", border_style="purple"))
                if resp.get('tokens_used'):
                    console.print(f"\n[dim]📊 Токенов: {resp['tokens_used']} | Модель: {resp.get('model')}[/dim]")
        except CLIError as e:
            console.print(f"[bold red]❌ Ошибка AI:[/bold red] {e.message}")
            raise typer.Exit(6)