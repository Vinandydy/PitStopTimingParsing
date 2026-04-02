from karting_cli.main import app


def test_heats_list_success(cli_runner):
    result = cli_runner.invoke(app, ["heats", "list"])
    assert result.exit_code == 0
    assert "Гонка 1" in result.stdout


def test_heats_list_with_filters(cli_runner, mock_api):
    result = cli_runner.invoke(
        app,
        ["heats", "list", "--track", "1", "--type", "Race", "--champ", "OPEN2025", "--limit", "5"],
    )
    assert result.exit_code == 0
    params = mock_api["calls"][0]["params"]
    assert params["track"] == 1
    assert params["session_type"] == "Race"
    assert params["championship"] == "OPEN2025"


def test_heats_get_success(cli_runner):
    result = cli_runner.invoke(app, ["heats", "get", "100"])
    assert result.exit_code == 0
    assert "Гонка 1" in result.stdout


def test_heats_get_not_found(cli_runner):
    result = cli_runner.invoke(app, ["heats", "get", "999"])
    assert result.exit_code == 0
    assert "не найден" in result.stdout.lower()


def test_heats_latest_success(cli_runner, mock_api):
    result = cli_runner.invoke(app, ["heats", "latest", "--track", "1", "--limit", "2"])
    assert result.exit_code == 0
    params = mock_api["calls"][0]["params"]
    assert params["track"] == 1
