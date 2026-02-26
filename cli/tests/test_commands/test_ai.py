"""Тесты команд ai."""

import pytest
from typer.testing import CliRunner

from karting.__main__ import app

runner = CliRunner()


class TestAIInsight:
    """Тесты команды ai insight."""

    def test_ai_insight_with_heat(self, mock_heats_endpoint, mock_ai_endpoint, cli_runner, mock_api_base, monkeypatch):
        """Тест AI-анализа заезда."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "insight", "--heat", "135"])

        assert result.exit_code == 0
        assert "Анализирую" in result.stdout or "🔍" in result.stdout
        # Проверка что AI endpoint был вызван
        assert mock_ai_endpoint.calls[0].request.method == "POST"

    def test_ai_insight_with_driver(self, mock_drivers_endpoint, mock_results_endpoint, mock_ai_endpoint, cli_runner,
                                    mock_api_base, monkeypatch):
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
        assert "Укажите" in result.stdout or "❌" in result.stdout

    def test_ai_insight_custom_prompt(self, mock_heats_endpoint, mock_ai_endpoint, cli_runner, mock_api_base,
                                      monkeypatch):
        """Тест с кастомным промптом."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, [
            "ai", "insight",
            "--heat", "135",
            "--prompt", "Кто показал лучший старт?"
        ])

        assert result.exit_code == 0
        # Проверка что промпт передан в AI
        request_body = mock_ai_endpoint.calls[0].request.read()
        assert "Кто показал лучший старт?" in request_body.decode()

    def test_ai_insight_with_model(self, mock_heats_endpoint, mock_ai_endpoint, cli_runner, mock_api_base, monkeypatch):
        """Тест с указанием модели."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, [
            "ai", "insight",
            "--heat", "135",
            "--model", "qwen2.5:3b"
        ])

        assert result.exit_code == 0
        request_body = mock_ai_endpoint.calls[0].request.read()
        assert "qwen2.5:3b" in request_body.decode()


class TestAIAnalyzeHeat:
    """Тесты команды ai analyze-heat."""

    def test_analyze_heat_success(self, mock_heats_endpoint, mock_ai_endpoint, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного анализа заезда."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["ai", "analyze-heat", "135"])

        assert result.exit_code == 0
        assert "Анализирую" in result.stdout or "🏁" in result.stdout

    def test_analyze_heat_with_focus(self, mock_heats_endpoint, mock_ai_endpoint, cli_runner, mock_api_base,
                                     monkeypatch):
        """Тест анализа с фокусом."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, [
            "ai", "analyze-heat", "135",
            "--focus", "strategy"
        ])

        assert result.exit_code == 0

    def test_analyze_heat_not_found(self, mock_heats_endpoint, cli_runner, mock_api_base, monkeypatch, respx):
        """Тест заезда, который не найден."""
        import respx
        from httpx import Response

        with respx.mock(base_url=mock_api_base) as mock:
            mock.get("/heats/999/").mock(
                return_value=Response(404, json={"error": "Not found"})
            )
            monkeypatch.setenv("KARTING_API_URL", mock_api_base)

            result = cli_runner.invoke(app, ["ai", "analyze-heat", "999"])

            assert result.exit_code != 0


class TestAIModels:
    """Тесты команды ai models."""

    def test_ai_models_success(self, cli_runner, mock_api_base, monkeypatch, respx):
        """Тест получения списка моделей."""
        import respx
        from httpx import Response

        with respx.mock(base_url="http://localhost:11434") as mock:
            mock.get("/api/tags").mock(
                return_value=Response(200, json={
                    "models": [
                        {"name": "qwen2.5:7b", "size": 4700000000},
                        {"name": "qwen2.5:3b", "size": 2000000000},
                    ]
                })
            )
            monkeypatch.setenv("KARTING_API_URL", mock_api_base)

            result = cli_runner.invoke(app, ["ai", "models"])

            assert result.exit_code == 0
            assert "qwen2.5:7b" in result.stdout or "Модели" in result.stdout