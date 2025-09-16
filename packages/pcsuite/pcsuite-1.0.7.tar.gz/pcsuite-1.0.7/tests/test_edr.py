import os
import yaml
from typer.testing import CliRunner
import pytest


def test_edr_detect_cli_with_mocked_events(monkeypatch, tmp_path):
    # Create a couple of Sigma-like rules
    rule1 = {
        "title": "Suspicious Keyword",
        "detection": {"contains": {"Message": ["Mimikatz", "Cobalt"]}},
    }
    rule2 = {
        "title": "Regex Test",
        "detection": {"regex": {"Message": ["Mimi"]}},
    }
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "rule.yml").write_text(yaml.safe_dump(rule1), encoding="utf-8")
    (rules_dir / "rule2.yml").write_text(yaml.safe_dump(rule2), encoding="utf-8")

    # Mock security events
    events = [
        {"Message": "User ran Mimikatz on host"},
        {"Message": "Normal logon"},
    ]
    from pcsuite.security import logs

    monkeypatch.setattr(logs, "get_security_events", lambda limit=200: events)

    from pcsuite.cli.main import app

    runner = CliRunner()
    res = runner.invoke(app, ["edr", "detect", "--rules", str(rules_dir), "--limit", "50"])
    assert res.exit_code == 0
    assert "Suspicious Keyword" in res.output
    assert "Regex Test" in res.output


@pytest.mark.skipif(os.name != "nt", reason="Windows-only file ops variability")
def test_edr_quarantine_file_dry_run(monkeypatch, tmp_path):
    # Prepare a file
    f = tmp_path / "sample.txt"
    f.write_text("data", encoding="utf-8")

    from pcsuite.cli.main import app
    runner = CliRunner()
    res = runner.invoke(app, ["edr", "quarantine-file", str(f), "--dry-run"])
    assert res.exit_code == 0
    assert "Dry-run" in res.output
