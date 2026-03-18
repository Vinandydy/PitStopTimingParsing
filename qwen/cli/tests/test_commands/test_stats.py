"""Тесты команд stats."""
import pytest
from typer.testing import CliRunner
from karting.__main__ import app

runner = CliRunner()


class TestStatsDriver:
    """Тесты команды stats driver."""

    def test_stats_driver_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешной статистики пилота."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["stats", "driver", "177"])
        assert result.exit_code == 0
        assert "177" in result.stdout or "Статистика" in result.stdout

    def test_stats_driver_with_period(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест статистики с периодом."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["stats", "driver", "177", "--period", "30d"])
        assert result.exit_code == 0

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