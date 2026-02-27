# cli/karting/commands/ai.py

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from karting.client import APIClient
from karting.exceptions import CLIError

app = typer.Typer(help="🤖 AI-инсайты")
console = Console()


@app.command("analyze-heat")
def analyze_heat(
        heat_id: int = typer.Argument(..., help="ID заезда для анализа"),
        focus: str = typer.Option(
            "all", "--focus", "-f",
            help="Фокус: all, podium, strategy, stability, advice",
            case_sensitive=False
        ),
        model: str = typer.Option("qwen2.5:7b", "--model", "-m", help="Модель Ollama"),
):
    """🏁 Детальный анализ заезда через QWEN"""

    with APIClient() as api, console.status("[bold green]Загрузка данных...[/bold green]"):
        heat = api.get_heat(heat_id)

    # Формируем контекст для backend (только нужные поля)
    context = {
        'heat_id': heat.get('id'),
        'name': heat.get('name'),
        'track_name': heat.get('track_name'),
        'scheduled_at': heat.get('scheduled_at'),
        'session_type': heat.get('session_type'),
        'championship': heat.get('championship'),
        'laps_count': heat.get('laps_count'),
        'results': heat.get('results', [])[:15],  # Топ-15 для контекста
    }

    # Промпты в зависимости от фокуса
    prompts = {
        "all": "Проанализируй заезд полностью: подиум, лучший круг, стратегия, стабильность, советы.",
        "podium": "Сделай акцент на анализе подиума и лучших кругах топ-3.",
        "strategy": "Сделай акцент на стратегии пит-стопов (S1/S2/S3) и времени смены карта.",
        "stability": "Сделай акцент на стабильности пилотов (разница лучший/средний круг).",
        "advice": "Сделай акцент на конкретных измеримых советах для улучшения.",
    }

    user_prompt = prompts.get(focus, prompts["all"])

    payload = {
        'prompt': user_prompt,
        'context': context,
        'model': model,
        'temperature': 0.1,  # меньше креатива, больше фактов
        'max_tokens': 768,  # больше токенов для детального ответа
    }

    heat_name = heat.get('name', f'Заезд #{heat_id}')
    console.print(f"\n[bold cyan]🏁 Анализирую:[/bold cyan] {heat_name}")
    console.print(f"[dim]Фокус: {focus} | Модель: {model}[/dim]\n")

    with console.status("[bold green]🤔 Генерация...[/bold green]"):
        try:
            with APIClient() as api:
                resp = api.request("POST", "/ai/generate/", json_data=payload, use_cache=False)

            insight = resp.get('insight', 'Нет ответа')

            # ✅ Правильный вывод Panel (не через +)
            console.print()
            console.print(
                Panel(
                    Markdown(insight),
                    title="🏁 Анализ заезда",
                    border_style="blue",
                    width=min(console.width, 110)
                )
            )

            if resp.get('tokens_used'):
                console.print(
                    f"\n[dim]📊 Токенов: {resp['tokens_used']} | Время: {resp.get('duration_ms', 0) / 1000:.1f}сек[/dim]")

        except CLIError as e:
            console.print(f"[bold red]❌ Ошибка:[/bold red] {e.message}")
            raise typer.Exit(6)