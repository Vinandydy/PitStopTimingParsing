"""Конфигурация CLI: API URL, кэш, формат вывода."""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from decouple import config as env_config

from karting import __version__

CONFIG_DIR = Path.home() / ".karting"
CONFIG_FILE = CONFIG_DIR / "config.json"


class CLIConfig(BaseModel):
    api_base_url: str = Field(default="http://localhost:8000/api")
    api_timeout: int = Field(default=30, ge=5, le=300)
    api_token: Optional[str] = None
    default_format: str = Field(default="table", pattern="^(table|json|csv)$")
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    verbose: bool = False

    @field_validator('api_base_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Удаляет trailing slash из URL."""
        return v.rstrip('/')

    @classmethod
    def load(cls) -> 'CLIConfig':
        env_url = env_config('KARTING_API_URL', default=None)

        file_cfg = {}
        if CONFIG_FILE.exists():
            import json
            try:
                file_cfg = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
            except:
                pass

        return cls(
            api_base_url=env_url or file_cfg.get('api_base_url') or cls.model_fields['api_base_url'].default,
            api_token=env_config('KARTING_API_TOKEN', default=file_cfg.get('api_token')),
            api_timeout=file_cfg.get('api_timeout', cls.model_fields['api_timeout'].default),
            default_format=file_cfg.get('default_format', cls.model_fields['default_format'].default),
            cache_enabled=file_cfg.get('cache_enabled', cls.model_fields['cache_enabled'].default),
            cache_ttl_seconds=file_cfg.get('cache_ttl_seconds', cls.model_fields['cache_ttl_seconds'].default),
            verbose=file_cfg.get('verbose', cls.model_fields['verbose'].default),
        )

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(self.model_dump_json(indent=2), encoding='utf-8')

    @property
    def headers(self) -> dict:
        h = {'User-Agent': f'karting-cli/{__version__}'}
        if self.api_token:
            h['Authorization'] = f'Bearer {self.api_token}'
        return h


_cfg = None


def get_config() -> CLIConfig:
    global _cfg
    if _cfg is None:
        _cfg = CLIConfig.load()
    return _cfg