"""Тесты команд stats."""
import pytest
from typer.testing import CliRunner
from qwen.cli.karting.__main__ import app

runner = CliRunner()


class TestStatsDriver:
    """Тесты команды stats driver."""

    def test_stats_driver_json_format(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест вывода статистики в JSON."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["stats", "driver", "177", "--format", "json"])
        assert result.exit_code == 0
        assert "{" in result.stdout

    def test_stats_driver_not_found(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест пилота, который не найден."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["stats", "driver", "999"])
        assert result.exit_code != 0
        assert "не найден" in result.stdout.lower() or "❌" in result.stdout