from pathlib import Path

from karting_cli.main import app


def test_export_drivers_to_file(cli_runner, tmp_path):
    out = Path(tmp_path) / "drivers.json"
    result = cli_runner.invoke(app, ["export", "drivers", "--format", "json", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "Иван Петров" in out.read_text(encoding="utf-8")


def test_export_karts_to_file(cli_runner, tmp_path):
    out = Path(tmp_path) / "karts.csv"
    result = cli_runner.invoke(app, ["export", "karts", "--format", "csv", "--output", str(out), "--active"])
    assert result.exit_code == 0
    assert out.exists()
    assert "number" in out.read_text(encoding="utf-8")


def test_export_heats_to_file(cli_runner, tmp_path):
    out = Path(tmp_path) / "heats.json"
    result = cli_runner.invoke(
        app,
        ["export", "heats", "--format", "json", "--output", str(out)],
    )
    assert result.exit_code == 0
    assert out.exists()
    assert "Гонка 1" in out.read_text(encoding="utf-8")
