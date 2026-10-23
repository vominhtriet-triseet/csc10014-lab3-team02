from pathlib import Path

from assistant_core import __main__ as cli
from assistant_core.config import Settings


def test_cli_builds_service_and_answers_help(monkeypatch, capsys):
    data_dir = Path(__file__).resolve().parents[1] / "data"
    settings = Settings(data_dir=data_dir)
    monkeypatch.setattr(cli, "load_settings", lambda: settings)

    exit_code = cli.main(["help"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "office locations" in captured.out
    assert '"intent": "help"' in captured.err
