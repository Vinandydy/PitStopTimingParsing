"""Тесты команд heats."""
import pytest
from typer.testing import CliRunner
from karting.__main__ import app

runner = CliRunner()


class TestHeatsList:
    """Тесты команды heats list."""

    def test_heats_list_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного получения списка заездов."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "list"])
        assert result.exit_code == 0
        assert "Заезды" in result.stdout or "🏁" in result.stdout

    def test_heats_list_with_filters(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест фильтрации заездов."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "list", "--champ", "ГГ2026", "--type", "Race", "--limit", "10"])
        assert result.exit_code == 0
        call_params = mock_api_client['calls'][0]['params']
        assert call_params.get('championship') == "ГГ2026"
        assert call_params.get('session_type') == "Race"
        assert call_params.get('limit') == 10

    def test_heats_list_json_format(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест вывода в JSON формате."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "list", "--format", "json"])
        assert result.exit_code == 0
        assert "{" in result.stdout

    def test_heats_list_empty(self, mock_api_client_empty, cli_runner, mock_api_base, monkeypatch):
        """Тест пустого списка заездов."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "list"])
        assert result.exit_code == 0
        assert "Ничего не найдено" in result.stdout or "⚠️" in result.stdout

    def test_heats_list_invalid_limit(self, cli_runner, mock_api_base, monkeypatch):
        """Тест невалидного limit."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "list", "--limit", "500"])
        assert result.exit_code == 2
        assert "limit" in result.stdout.lower() or "limit" in result.stderr.lower()

    def test_heats_list_api_error(self, mock_api_client_error, cli_runner, mock_api_base, monkeypatch):
        """Тест ошибки API."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "list"])
        assert result.exit_code != 0


class TestHeatsDetail:
    """Тесты команды heats detail."""

    def test_heats_detail_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного получения деталей заезда."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "detail", "135"])
        assert result.exit_code == 0
        assert "135" in result.stdout or "🏁" in result.stdout

    def test_heats_detail_not_found(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест заезда, который не найден."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "detail", "999"])
        assert result.exit_code == 5
        assert "не найден" in result.stdout.lower() or "❌" in result.stdout

    def test_heats_detail_json_format(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест вывода деталей в JSON."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "detail", "135", "--format", "json"])
        assert result.exit_code == 0
        assert "{" in result.stdout

    def test_heats_detail_with_results(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест деталей заезда с результатами."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["heats", "detail", "135"])
        assert result.exit_code == 0
        assert "koker57" in result.stdout or "результат" in result.stdout.lower()