"""Тесты команд results."""
import pytest
from typer.testing import CliRunner
from karting.__main__ import app

runner = CliRunner()


class TestResultsList:
    """Тесты команды results list."""

    def test_results_list_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного получения результатов."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["results", "list"])

        assert result.exit_code == 0
        assert "Результаты" in result.stdout or "📊" in result.stdout

    def test_results_list_with_filters(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест фильтрации результатов."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, [
            "results", "list",
            "--heat", "135",
            "--driver", "177",
            "--limit", "20"
        ])

        assert result.exit_code == 0
        call_params = mock_api_client['calls'][0]['params']
        assert call_params.get('heat') == 135
        assert call_params.get('driver') == 177
        assert call_params.get('limit') == 20

    def test_results_list_json_format(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест вывода в JSON формате."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["results", "list", "--format", "json"])

        assert result.exit_code == 0
        assert "{" in result.stdout