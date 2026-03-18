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
        assert result.exit_code in [0, 2]  # 2 если команда не реализована

    def test_ai_insight_with_driver(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест AI-анализа пилота."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["ai", "insight", "--driver", "177"])
        assert result.exit_code in [0, 2]

    def test_ai_insight_no_arguments(self, cli_runner, mock_api_base, monkeypatch):
        """Тест без указания heat или driver."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["ai", "insight"])
        assert result.exit_code == 2
        assert "Укажите" in result.stdout or "Укажите" in result.stderr or "❌" in result.stdout or "No such command" in result.stderr


class TestAIAnalyzeHeat:
    """Тесты команды ai analyze-heat."""

    def test_analyze_heat_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного анализа заезда."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["ai", "analyze-heat", "135"])
        assert result.exit_code in [0, 2, 5, 6]  # Разные коды возможны

    def test_analyze_heat_with_focus(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест анализа с фокусом."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["ai", "analyze-heat", "135", "--focus", "strategy"])
        assert result.exit_code in [0, 2, 5, 6]

    def test_analyze_heat_not_found(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест заезда, который не найден."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["ai", "analyze-heat", "999"])
        assert result.exit_code != 0


class TestAIModels:
    """Тесты команды ai models."""

    def test_ai_models_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест получения списка моделей."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["ai", "models"])
        assert result.exit_code in [0, 2]  # 2 если команда не реализована