"""HTTP-клиент для взаимодействия с DRF API."""

import json
import time
from pathlib import Path
from typing import Any

from httpx import Client, HTTPStatusError, RequestError

from .config import CLIConfig, get_config
from .exceptions import APIConnectionError, APIResourceNotFound, CLIError

CACHE_DIR = Path.home() / ".karting" / "cache"


class APIClient:
    """Клиент с кэшированием и обработкой ошибок."""

    def __init__(self, config: CLIConfig | None = None):
        self.cfg = config or get_config()
        self.client = Client(
            base_url=self.cfg.api_base_url,
            headers=self.cfg.headers,
            timeout=self.cfg.api_timeout,
            follow_redirects=True,
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()

    def _cache_key(self, endpoint: str, params: dict[str, Any] | None) -> str:
        import hashlib
        payload = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(payload.encode()).hexdigest()

    def _get_cached(self, key: str) -> dict[str, Any] | None:
        if not self.cfg.cache_enabled:
            return None
        try:
            f = CACHE_DIR / f"{key}.json"
            if not f.exists():
                return None
            data = json.loads(f.read_text(encoding='utf-8'))
            if time.time() - data['ts'] < self.cfg.cache_ttl_seconds:
                return data['body']
            f.unlink(missing_ok=True)
        except:
            pass
        return None

    def _set_cached(self, key: str, body: dict[str, Any]):
        if not self.cfg.cache_enabled:
            return
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            (CACHE_DIR / f"{key}.json").write_text(
                json.dumps({'body': body, 'ts': time.time()}, ensure_ascii=False),
                encoding='utf-8'
            )
        except:
            pass

    def request(self, method: str, endpoint: str, params: dict[str, Any] | None = None,
                json_data: dict[str, Any] | None = None, use_cache: bool = True) -> dict[str, Any]:
        cache_key = self._cache_key(endpoint, params) if method == "GET" and use_cache else None

        if cache_key:
            cached = self._get_cached(cache_key)
            if cached:
                if self.cfg.verbose:
                    from rich.console import Console
                    Console().print("[dim]✓ кэш[/dim]")
                return cached

        try:
            resp = self.client.request(method, endpoint, params=params, json=json_data)
            resp.raise_for_status()
            result = resp.json() if resp.content else {}
            if cache_key:
                self._set_cached(cache_key, result)
            return result
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise APIResourceNotFound("Ресурс", endpoint)
            raise CLIError(f"API {e.response.status_code}", exit_code=2, details=e.response.text[:150])
        except RequestError as e:
            # ✅ Исправление: явно поднимаем APIConnectionError
            raise APIConnectionError(self.cfg.api_base_url, e)
        except Exception as e:
            # ✅ Ловим любые другие исключения как ConnectionError
            raise APIConnectionError(self.cfg.api_base_url, e)

    # Convenience-методы под ваши ViewSets
    def list_heats(self, **kw) -> dict[str, Any]:
        return self.request("GET", "/heats/", params=kw)

    def get_heat(self, id: int) -> dict[str, Any]:
        return self.request("GET", f"/heats/{id}/")

    def list_drivers(self, **kw) -> dict[str, Any]:
        return self.request("GET", "/drivers/", params=kw)

    def get_driver(self, id: int) -> dict[str, Any]:
        return self.request("GET", f"/drivers/{id}/")

    def list_results(self, **kw) -> dict[str, Any]:
        return self.request("GET", "/results/", params=kw)

    def list_tracks(self, **kw) -> dict[str, Any]:
        return self.request("GET", "/tracks/", params=kw)
