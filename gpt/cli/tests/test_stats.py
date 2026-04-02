from karting_cli.main import app


def test_stats_summary_success(cli_runner):
    result = cli_runner.invoke(app, ["stats", "summary"])
    assert result.exit_code == 0
    assert "Общая статистика" in result.stdout
    assert "Всего заездов" in result.stdout
