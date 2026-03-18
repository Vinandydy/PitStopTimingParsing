"""Тесты конфигурации CLI."""

import pytest
import json
from pathlib import Path

from karting.config import CLIConfig, CONFIG_DIR, CONFIG_FILE


class TestCLIConfig:
    """Тесты класса CLIConfig."""

    def test_load_defaults(self, tmp_path, monkeypatch):
        """Тест загрузки конфигурации по умолчанию."""
        # Временно меняем директорию конфига
        monkeypatch.setattr("karting.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("karting.config.CONFIG_FILE", tmp_path / "config.json")

        config = CLIConfig.load()

        assert config.api_base_url == "http://localhost:8000/api"
        assert config.api_timeout == 30
        assert config.default_format == "table"
        assert config.cache_enabled is True

    def test_load_from_env(self, tmp_path, monkeypatch):
        """Тест загрузки из переменных окружения."""
        monkeypatch.setattr("karting.config.CONFIG_DIR", tmp_path)
        monkeypatch.setenv("KARTING_API_URL", "http://custom-api:8000/api")

        config = CLIConfig.load()

        assert config.api_base_url == "http://custom-api:8000/api"

    def test_load_from_file(self, tmp_path, monkeypatch):
        """Тест загрузки из файла конфигурации."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "api_base_url": "http://file-api:8000/api",
            "api_timeout": 60,
            "default_format": "json"
        }))

        monkeypatch.setattr("karting.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("karting.config.CONFIG_FILE", config_file)

        config = CLIConfig.load()

        assert config.api_base_url == "http://file-api:8000/api"
        assert config.api_timeout == 60
        assert config.default_format == "json"

    def test_save_config(self, tmp_path, monkeypatch):
        """Тест сохранения конфигурации."""
        monkeypatch.setattr("karting.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("karting.config.CONFIG_FILE", tmp_path / "config.json")

        config = CLIConfig(api_base_url="http://test:8000/api")
        config.save()

        assert (tmp_path / "config.json").exists()
        saved = json.loads((tmp_path / "config.json").read_text())
        assert saved["api_base_url"] == "http://test:8000/api"

    def test_headers_with_token(self):
        """Тест заголовков с токеном."""
        config = CLIConfig(api_token="test_token_123")
        headers = config.headers

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_123"
        assert "User-Agent" in headers

    def test_headers_without_token(self):
        """Тест заголовков без токена."""
        config = CLIConfig()
        headers = config.headers

        assert "Authorization" not in headers
        assert "User-Agent" in headers

    def test_validate_url(self):
        """Тест валидации URL."""
        config = CLIConfig(api_base_url="http://test:8000/api/")
        assert config.api_base_url == "http://test:8000/api"  # trailing slash removed

    def test_api_timeout_bounds(self):
        """Тест границ api_timeout."""
        # Минимальное значение
        config = CLIConfig(api_timeout=5)
        assert config.api_timeout == 5

        # Максимальное значение
        config = CLIConfig(api_timeout=300)
        assert config.api_timeout == 300