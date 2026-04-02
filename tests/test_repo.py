import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args, cwd):
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Command failed: {' '.join(args)}\n"
            f"cwd: {cwd}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def test_gpt_backend():
    run_cmd([sys.executable, "manage.py", "test"], REPO_ROOT / "gpt")


def test_gpt_cli():
    run_cmd([sys.executable, "-m", "pytest", "-q"], REPO_ROOT / "gpt" / "cli")


def test_qwen_backend():
    run_cmd([sys.executable, "manage.py", "test"], REPO_ROOT / "qwen" / "backend")


def test_qwen_cli():
    run_cmd([sys.executable, "-m", "pytest", "-q"], REPO_ROOT / "qwen" / "cli")
