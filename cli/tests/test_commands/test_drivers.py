"""Тесты команд drivers."""
import pytest
from typer.testing import CliRunner
from karting.__main__ import app

runner = CliRunner()


class TestDriversList:
    """Тесты команды drivers list."""

    def test_drivers_list_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного получения списка пилотов."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["drivers", "list"])

        assert result.exit_code == 0
        assert "Пилоты" in result.stdout or "👤" in result.stdout

    def test_drivers_list_with_search(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест поиска пилотов."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["drivers", "list", "--search", "koker"])

        assert result.exit_code == 0
        call_params = mock_api_client['calls'][0]['params']
        assert call_params.get('search') == 'koker'

    def test_drivers_list_json_format(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест вывода в JSON формате."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["drivers", "list", "--format", "json"])

        assert result.exit_code == 0
        assert "{" in result.stdout


class TestDriversDetail:
    """Тесты команды drivers detail."""

    def test_drivers_detail_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного получения деталей пилота."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["drivers", "detail", "177"])

        assert result.exit_code == 0
        assert "177" in result.stdout or "koker57" in result.stdout

    def test_drivers_detail_not_found(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест пилота, который не найден."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)

        result = cli_runner.invoke(app, ["drivers", "detail", "999"])

        assert result.exit_code != 0
        assert "не найден" in result.stdout.lower() or "❌" in result.stdout