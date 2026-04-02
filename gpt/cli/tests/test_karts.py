from karting_cli.main import app


def test_karts_list_success(cli_runner):
    result = cli_runner.invoke(app, ["karts", "list"])
    assert result.exit_code == 0
    assert "Карты" in result.stdout


def test_karts_list_active_filter(cli_runner, mock_api):
    result = cli_runner.invoke(app, ["karts", "list", "--track", "1", "--active", "--limit", "5"])
    assert result.exit_code == 0
    params = mock_api["calls"][0]["params"]
    assert params["track"] == 1
    assert params["is_active"] is True


def test_karts_get_success(cli_runner):
    result = cli_runner.invoke(app, ["karts", "get", "3"])
    assert result.exit_code == 0
    assert "Карт #6" in result.stdout


def test_karts_stats_success(cli_runner):
    result = cli_runner.invoke(app, ["karts", "stats", "3"])
    assert result.exit_code == 0
    assert "Статистика" in result.stdout


def test_karts_active_success(cli_runner, mock_api):
    result = cli_runner.invoke(app, ["karts", "active", "--track", "1"])
    assert result.exit_code == 0
    params = mock_api["calls"][0]["params"]
    assert params["track"] == 1
    assert params["is_active"] is True
