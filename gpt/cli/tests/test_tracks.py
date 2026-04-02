from karting_cli.main import app


def test_tracks_list_success(cli_runner):
    result = cli_runner.invoke(app, ["tracks", "list"])
    assert result.exit_code == 0
    assert "Premium" in result.stdout
    assert "Треки" in result.stdout
