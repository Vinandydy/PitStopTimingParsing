"""Тесты команд export."""
import pytest
import json
import csv
from pathlib import Path
from typer.testing import CliRunner
from karting.__main__ import app

runner = CliRunner()


class TestExportCSV:
    """Тесты команды export csv."""

    def test_export_csv_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch, tmp_path):
        """Тест успешного экспорта в CSV."""
        output_file = tmp_path / "export.csv"
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["export", "csv", "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0

    def test_export_csv_with_filters(self, mock_api_client, cli_runner, mock_api_base, monkeypatch, tmp_path):
        """Тест экспорта с фильтрами."""
        output_file = tmp_path / "filtered.csv"
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["export", "csv", "--heat", "135", "--driver", "177", "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        call_params = mock_api_client['calls'][0]['params']
        assert call_params.get('heat') == 135
        assert call_params.get('driver') == 177


class TestExportJSON:
    """Тесты команды export json."""

    def test_export_json_success(self, mock_api_client, cli_runner, mock_api_base, monkeypatch, tmp_path):
        """Тест успешного экспорта в JSON."""
        output_file = tmp_path / "export.json"
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["export", "json", "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert isinstance(data, list) or isinstance(data, dict)

    def test_export_json_with_filters(self, mock_api_client, cli_runner, mock_api_base, monkeypatch, tmp_path):
        """Тест экспорта JSON с фильтрами."""
        output_file = tmp_path / "filtered.json"
        monkeypatch.setenv("KARTING_API_URL", mock_api_base)
        result = cli_runner.invoke(app, ["export", "json", "--heat", "135", "--output", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()