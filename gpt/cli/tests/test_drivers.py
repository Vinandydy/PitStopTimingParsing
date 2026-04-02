from karting_cli.main import app


def test_drivers_list_success(cli_runner):
    result = cli_runner.invoke(app, ["drivers", "list"])
    assert result.exit_code == 0
    assert "Иван Петров" in result.stdout


def test_drivers_list_with_filters(cli_runner, mock_api):
    result = cli_runner.invoke(app, ["drivers", "list", "--track", "1", "--search", "Иван", "--limit", "5"])
    assert result.exit_code == 0
    params = mock_api["calls"][0]["params"]
    assert params["track"] == 1
    assert params["search"] == "Иван"


def test_drivers_get_success(cli_runner):
    result = cli_runner.invoke(app, ["drivers", "get", "10"])
    assert result.exit_code == 0
    assert "Иван Петров" in result.stdout


def test_drivers_get_not_found(cli_runner):
    result = cli_runner.invoke(app, ["drivers", "get", "999"])
    assert result.exit_code == 0
    assert "не найден" in result.stdout.lower()


def test_drivers_stats_success(cli_runner):
    result = cli_runner.invoke(app, ["drivers", "stats", "10"])
    assert result.exit_code == 0
    assert "Статистика" in result.stdout


def test_drivers_top_success(cli_runner):
    result = cli_runner.invoke(app, ["drivers", "top", "--limit", "3"])
    assert result.exit_code == 0
    assert "Иван Петров" in result.stdout
