from karting_cli.main import app


def test_config_set_and_show(cli_runner):
    result_set = cli_runner.invoke(app, ["config", "--set-api", "http://localhost:9999/api"])
    assert result_set.exit_code == 0
    assert "API URL установлен" in result_set.stdout

    result_show = cli_runner.invoke(app, ["config", "--show"])
    assert result_show.exit_code == 0
    assert "http://localhost:9999/api" in result_show.stdout


def test_config_reset(cli_runner):
    cli_runner.invoke(app, ["config", "--set-api", "http://localhost:9999/api"])
    result = cli_runner.invoke(app, ["config", "--reset"])
    assert result.exit_code == 0
    assert "сброшена" in result.stdout.lower()
