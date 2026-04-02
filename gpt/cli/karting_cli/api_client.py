"""Клиент для работы с REST API"""
import httpx
from typing import Optional, Dict, Any, List
from .config import Config


class APIClient:
    """Клиент для взаимодействия с DRF API"""

    def __init__(self):
        self.config = Config()
        self.base_url = self.config.get("api_url")
        self.timeout = self.config.get("timeout")
        self.verbose = self.config.get("verbose")

    def _log(self, message: str):
        """Логирование в verbose режиме"""
        if self.verbose:
            print(f"[DEBUG] {message}")

    def _get_client(self) -> httpx.Client:
        """Создает HTTP клиент"""
        return httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Выполняет HTTP запрос"""
        self._log(f"{method.upper()} {endpoint}")

        with self._get_client() as client:
            try:
                response = client.request(method, endpoint, **kwargs)
                response.raise_for_status()

                if response.status_code == 204:
                    return {"success": True}

                return response.json()

            except httpx.HTTPStatusError as e:
                print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"❌ Connection Error: {e}")
                return None
            except Exception as e:
                print(f"❌ Unexpected Error: {e}")
                return None

    # === TRACKS ===
    def get_tracks(self) -> List[Dict]:
        """Получает список треков"""
        result = self._make_request("GET", "/tracks/")
        return result.get("results", []) if result else []

    # === DRIVERS ===
    def get_drivers(
        self,
        track: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Dict]:
        """Получает список гонщиков"""
        params = {"page": page, "page_size": page_size}
        if track:
            params["track"] = track
        if search:
            params["search"] = search

        result = self._make_request("GET", "/drivers/", params=params)
        return result.get("results", []) if result else []

    def get_driver(self, driver_id: int) -> Optional[Dict]:
        """Получает информацию о гонщике"""
        return self._make_request("GET", f"/drivers/{driver_id}/")

    # === KARTS ===
    def get_karts(
        self,
        track: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Dict]:
        """Получает список картов"""
        params = {"page": page, "page_size": page_size}
        if track:
            params["track"] = track
        if is_active is not None:
            params["is_active"] = is_active

        result = self._make_request("GET", "/karts/", params=params)
        return result.get("results", []) if result else []

    def get_kart(self, kart_id: int) -> Optional[Dict]:
        """Получает информацию о карте"""
        return self._make_request("GET", f"/karts/{kart_id}/")

    # === HEATS ===
    def get_heats(
        self,
        track: Optional[int] = None,
        session_type: Optional[str] = None,
        championship: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Dict]:
        """Получает список заездов"""
        params = {"page": page, "page_size": page_size}
        if track:
            params["track"] = track
        if session_type:
            params["session_type"] = session_type
        if championship:
            params["championship"] = championship

        result = self._make_request("GET", "/heats/", params=params)
        return result.get("results", []) if result else []

    def get_heat(self, heat_id: int) -> Optional[Dict]:
        """Получает детальную информацию о заезде"""
        return self._make_request("GET", f"/heats/{heat_id}/")
