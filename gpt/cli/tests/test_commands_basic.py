from karting_cli.main import app


def test_root_help(cli_runner):
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "tracks" in result.stdout
    assert "drivers" in result.stdout
    assert "karts" in result.stdout
    assert "heats" in result.stdout
    assert "stats" in result.stdout
    assert "export" in result.stdout
    assert "parser" not in result.stdout
    assert "ai" not in result.stdout


def test_version(cli_runner):
    result = cli_runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.stdout
