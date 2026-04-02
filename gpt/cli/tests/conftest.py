from pathlib import Path

import pytest
from typer.testing import CliRunner

from karting_cli.api_client import APIClient
from karting_cli.config import Config


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    Config.CONFIG_DIR = Path(tmp_path) / ".timing-cli"
    Config.CONFIG_FILE = Config.CONFIG_DIR / "config.json"


@pytest.fixture()
def cli_runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_api(monkeypatch):
    calls = []
    tracks = [{"id": 1, "slug": "premium", "name": "Premium"}]
    drivers = [{
        "id": 10,
        "external_id": 159315,
        "name": "Иван Петров",
        "team": "Red",
        "track_name": "Premium",
        "total_races": 12,
        "best_lap_ms": 28423,
        "avg_lap_ms": 29210,
    }]
    karts = [{
        "id": 3,
        "number": 6,
        "track_name": "Premium",
        "is_active": True,
        "total_races": 30,
        "best_lap_ms": 28111,
        "avg_lap_ms": 28990,
    }]
    heats = [{
        "id": 100,
        "external_id": 105535,
        "name": "Гонка 1",
        "track_name": "Premium",
        "scheduled_at": "2026-03-20T12:00:00+03:00",
        "session_type": "Race",
        "participants_count": 1,
        "championship": "OPEN2025",
        "laps_count": 12,
        "results": [{
            "position": 1,
            "driver_name": "Иван Петров",
            "kart_number": 6,
            "best_lap_ms": 28423,
            "avg_lap_ms": 29210,
            "laps_completed": 12,
            "gap_to_leader_ms": 0,
        }],
    }]

    def get_tracks(self):
        calls.append({"method": "get_tracks", "params": {}})
        return tracks

    def get_drivers(self, **kwargs):
        calls.append({"method": "get_drivers", "params": kwargs})
        return drivers

    def get_driver(self, driver_id):
        calls.append({"method": "get_driver", "params": {"driver_id": driver_id}})
        return drivers[0] if driver_id == 10 else None

    def get_karts(self, **kwargs):
        calls.append({"method": "get_karts", "params": kwargs})
        return karts

    def get_kart(self, kart_id):
        calls.append({"method": "get_kart", "params": {"kart_id": kart_id}})
        return karts[0] if kart_id == 3 else None

    def get_heats(self, **kwargs):
        calls.append({"method": "get_heats", "params": kwargs})
        return heats

    def get_heat(self, heat_id):
        calls.append({"method": "get_heat", "params": {"heat_id": heat_id}})
        return heats[0] if heat_id == 100 else None

    monkeypatch.setattr(APIClient, "get_tracks", get_tracks)
    monkeypatch.setattr(APIClient, "get_drivers", get_drivers)
    monkeypatch.setattr(APIClient, "get_driver", get_driver)
    monkeypatch.setattr(APIClient, "get_karts", get_karts)
    monkeypatch.setattr(APIClient, "get_kart", get_kart)
    monkeypatch.setattr(APIClient, "get_heats", get_heats)
    monkeypatch.setattr(APIClient, "get_heat", get_heat)

    return {"calls": calls}
