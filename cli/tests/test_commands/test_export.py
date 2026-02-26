"""Тесты команд ai."""
import pytest
from typer.testing import CliRunner
from karting.__main__ import app

runner = CliRunner()


class TestAIInsight:
    """Тесты команды ai insight."""

    def test_ai_insight_with_heat(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест AI-анализа заезда."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "insight", "--heat", "135"])

        assert result.exit_code == 0
        assert "Анализирую" in result.stdout or "🔍" in result.stdout

    def test_ai_insight_with_driver(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест AI-анализа пилота."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "insight", "--driver", "177"])

        assert result.exit_code == 0
        assert "Анализирую" in result.stdout or "🔍" in result.stdout

    def test_ai_insight_no_arguments(self, cli_runner, mock_api_base, monkeypatch):
        """Тест без указания heat или driver."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "insight"])

        assert result.exit_code == 2
        # Typer выводит ошибки валидации в stderr
        assert "Укажите" in result.stdout or "Укажите" in result.stderr or "❌" in result.stdout

    def test_ai_insight_custom_prompt(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест с кастомным промптом."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, [
            "ai", "insight",
            "--heat", "135",
            "--prompt", "Кто показал лучший старт?"
        ])

        assert result.exit_code == 0

    def test_ai_insight_with_model(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест с указанием модели."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, [
            "ai", "insight",
            "--heat", "135",
            "--model", "qwen2.5:3b"
        ])

        assert result.exit_code == 0


class TestAIAnalyzeHeat:
    """Тесты команды ai analyze-heat."""

    def test_analyze_heat_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного анализа заезда."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "analyze-heat", "135"])

        assert result.exit_code == 0
        assert "Анализирую" in result.stdout or "🏁" in result.stdout

    def test_analyze_heat_with_focus(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест анализа с фокусом."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, [
            "ai", "analyze-heat", "135",
            "--focus", "strategy"
        ])

        assert result.exit_code == 0

    def test_analyze_heat_not_found(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест заезда, который не найден."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "analyze-heat", "999"])

        assert result.exit_code != 0
        assert "не найден" in result.stdout.lower() or "❌" in result.stdout


class TestAIModels:
    """Тесты команды ai models."""

    def test_ai_models_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест получения списка моделей."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "models"])

        assert result.exit_code == 0
        assert "Модели" in result.stdout or "qwen" in result.stdout.lower()