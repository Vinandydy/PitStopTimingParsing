"""Fixtures для тестов CLI."""
import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Тестовый runner для Typer CLI."""
    return CliRunner()


@pytest.fixture
def mock_api_base():
    """Базовый URL для моков API."""
    return "http://test-api:8000/api"


@pytest.fixture
def sample_heat_data():
    """Пример данных заезда для тестов."""
    return {
        "id": 135,
        "external_id": 106860,
        "name": "Гонщик года 5I - Гонка 60 кругов",
        "scheduled_at": "2026-02-24T22:20:00+03:00",
        "laps_count": 60,
        "session_type": "Race",
        "championship": "ГГ2026",
        "track": 1,
        "track_name": "Premium",
        "results": [
            {
                "id": 1,
                "position": 1,
                "driver": 177,
                "driver_name": "koker57",
                "kart": 2,
                "kart_number": 2,
                "best_lap_ms": 31285,
                "best_lap_formatted": "0:31.285",
                "avg_lap_ms": 33106,
                "avg_lap_formatted": "0:33.106",
                "laps_completed": 60,
                "s1_laps": 10,
                "s2_laps": 40,
                "s3_laps": 10,
            },
        ]
    }


@pytest.fixture
def sample_driver_data():
    """Пример данных пилота для тестов."""
    return {
        "id": 177,
        "external_id": 12345,
        "name": "koker57",
        "team": "Team Alpha",
        "track": 1,
        "track_name": "Premium",
        "total_races": 15,
        "avg_lap_ms": 33000,
        "best_lap_ms": 29500,
    }


@pytest.fixture
def sample_results_data():
    """Пример данных результатов для тестов."""
    return {
        "count": 3,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 1,
                "position": 1,
                "driver": 177,
                "driver_name": "koker57",
                "kart_number": 2,
                "best_lap_ms": 31285,
                "best_lap_formatted": "0:31.285",
                "avg_lap_ms": 33106,
                "laps_completed": 60,
                "heat": 135,
                "heat_name": "Гонщик года 5I - Гонка 60 кругов",
            }
        ]
    }


@pytest.fixture
def sample_tracks_data():
    """Пример данных треков для тестов."""
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {"id": 1, "slug": "premium", "name": "Premium"},
            {"id": 2, "slug": "sport", "name": "Sport"},
        ]
    }


@pytest.fixture
def mock_api_client(monkeypatch, sample_heat_data, sample_driver_data, sample_results_data, sample_tracks_data):
    """
    Мокируем методы APIClient через monkeypatch.
    """
    calls = []

    def mock_list_heats(**params):
        calls.append({'method': 'list_heats', 'params': params})
        return {"count": 1, "results": [sample_heat_data]}

    def mock_get_heat(heat_id):
        calls.append({'method': 'get_heat', 'heat_id': heat_id})
        if heat_id == 999:
            from karting.exceptions import APIResourceNotFound
            raise APIResourceNotFound(f"Heat {heat_id} not found")
        return sample_heat_data

    def mock_list_drivers(**params):
        calls.append({'method': 'list_drivers', 'params': params})
        return {"count": 1, "results": [sample_driver_data]}

    def mock_get_driver(driver_id):
        calls.append({'method': 'get_driver', 'driver_id': driver_id})
        if driver_id == 999:
            from karting.exceptions import APIResourceNotFound
            raise APIResourceNotFound(f"Driver {driver_id} not found")
        return sample_driver_data

    def mock_list_results(**params):
        calls.append({'method': 'list_results', 'params': params})
        return sample_results_data

    def mock_list_tracks(**params):
        calls.append({'method': 'list_tracks', 'params': params})
        return sample_tracks_data

    from karting import client
    monkeypatch.setattr(client.APIClient, 'list_heats', lambda self, **params: mock_list_heats(**params))
    monkeypatch.setattr(client.APIClient, 'get_heat', lambda self, heat_id: mock_get_heat(heat_id))
    monkeypatch.setattr(client.APIClient, 'list_drivers', lambda self, **params: mock_list_drivers(**params))
    monkeypatch.setattr(client.APIClient, 'get_driver', lambda self, driver_id: mock_get_driver(driver_id))
    monkeypatch.setattr(client.APIClient, 'list_results', lambda self, **params: mock_list_results(**params))
    monkeypatch.setattr(client.APIClient, 'list_tracks', lambda self, **params: mock_list_tracks(**params))

    return {'calls': calls}


@pytest.fixture
def mock_api_client_empty(monkeypatch):
    """Моки для пустого списка."""
    calls = []

    def mock_list_heats(**params):
        calls.append({'method': 'list_heats', 'params': params})
        return {"count": 0, "results": []}

    def mock_list_drivers(**params):
        calls.append({'method': 'list_drivers', 'params': params})
        return {"count": 0, "results": []}

    def mock_list_results(**params):
        calls.append({'method': 'list_results', 'params': params})
        return {"count": 0, "results": []}

    def mock_list_tracks(**params):
        calls.append({'method': 'list_tracks', 'params': params})
        return {"count": 0, "results": []}

    from karting import client
    monkeypatch.setattr(client.APIClient, 'list_heats', lambda self, **params: mock_list_heats(**params))
    monkeypatch.setattr(client.APIClient, 'list_drivers', lambda self, **params: mock_list_drivers(**params))
    monkeypatch.setattr(client.APIClient, 'list_results', lambda self, **params: mock_list_results(**params))
    monkeypatch.setattr(client.APIClient, 'list_tracks', lambda self, **params: mock_list_tracks(**params))

    return {'calls': calls}


@pytest.fixture
def mock_api_client_error(monkeypatch):
    """Моки для ошибки API."""
    calls = []

    def mock_list_heats(**params):
        calls.append({'method': 'list_heats', 'params': params})
        raise Exception("API Error")

    def mock_list_drivers(**params):
        calls.append({'method': 'list_drivers', 'params': params})
        raise Exception("API Error")

    def mock_list_results(**params):
        calls.append({'method': 'list_results', 'params': params})
        raise Exception("API Error")

    def mock_list_tracks(**params):
        calls.append({'method': 'list_tracks', 'params': params})
        raise Exception("API Error")

    from karting import client
    monkeypatch.setattr(client.APIClient, 'list_heats', lambda self, **params: mock_list_heats(**params))
    monkeypatch.setattr(client.APIClient, 'list_drivers', lambda self, **params: mock_list_drivers(**params))
    monkeypatch.setattr(client.APIClient, 'list_results', lambda self, **params: mock_list_results(**params))
    monkeypatch.setattr(client.APIClient, 'list_tracks', lambda self, **params: mock_list_tracks(**params))

    return {'calls': calls}