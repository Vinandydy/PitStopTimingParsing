"""Управление конфигурацией CLI"""
import os
import json
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv


class Config:
    """Класс для работы с конфигурацией CLI"""

    CONFIG_DIR = Path.home() / ".timing-cli"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        self._config = self._load_config()
        load_dotenv()

    def _load_config(self) -> dict:
        """Загружает конфигурацию из файла"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_config()

    def _default_config(self) -> dict:
        """Возвращает конфигурацию по умолчанию"""
        return {
            "api_url": os.getenv("TIMING_API_URL", "http://localhost:8002/api"),
            "timeout": int(os.getenv("TIMING_TIMEOUT", "30")),
            "verbose": os.getenv("TIMING_VERBOSE", "false").lower() == "true",
            "page_size": int(os.getenv("TIMING_PAGE_SIZE", "20")),
        }

    def save(self):
        """Сохраняет конфигурацию"""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Получает значение из конфигурации"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Устанавливает значение в конфигурации"""
        self._config[key] = value
        self.save()

    def reset(self):
        """Сбрасывает конфигурацию к значениям по умолчанию"""
        self._config = self._default_config()
        self.save()