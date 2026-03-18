"""Тесты команд tracks."""
import pytest
from typer.testing import CliRunner
from karting.__main__ import app

runner = CliRunner()


class TestTracksList:
    """Тесты команды tracks list."""

    def test_tracks_list_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест успешного получения списка треков."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["tracks", "list"])
        assert result.exit_code == 0
        assert "Треки" in result.stdout or "🗺️" in result.stdout
        assert "Premium" in result.stdout

    def test_tracks_list_with_search(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест поиска треков."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["tracks", "list", "--search", "Premium"])
        assert result.exit_code == 0
        call_params = mock_api_client['calls'][0]['params']
        assert call_params.get('search') == 'Premium'

    def test_tracks_list_json_format(self, mock_api_client, cli_runner, mock_api_base, monkeypatch):
        """Тест вывода в JSON формате."""
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["tracks", "list", "--format", "json"])
        assert result.exit_code == 0
        assert "{" in result.stdout