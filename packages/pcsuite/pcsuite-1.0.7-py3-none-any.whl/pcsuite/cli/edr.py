import json, os, sys
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from pcsuite.security import edr
from pcsuite.security import logs as seclogs
from pcsuite.security import canary as canary
from pcsuite.core import shell


app = typer.Typer(help="EDR prototype: status, isolation, triage, scans")
console = Console()


@app.command()
def status():
    data = edr.status()
    table = Table(title="EDR Status")
    table.add_column("Field"); table.add_column("Value")
    for k in ("product", "version", "os", "enrolled"):
        table.add_row(k, str(data.get(k)))
    fw = data.get("firewall", {})
    table.add_row("Firewall", ", ".join([f"{k}:{v}" for k, v in fw.items()]))
    console.print(table)


@app.command()
def isolate(
    enable: bool = typer.Option(..., help="Enable (True) or disable (False) network isolation"),
    dry_run: bool = typer.Option(True, help="Simulate; no changes"),
    block_outbound: bool = typer.Option(False, help="Also block outbound by policy with allowlist"),
    allow_host: list[str] = typer.Option(None, "--allow-host", "-a", help="Host/IP to allow when blocking outbound (repeatable)"),
    preset: list[str] = typer.Option(None, "--preset", help="Presets: ntp, winupdate, microsoft-basic, m365-core, teams, onedrive, edge-update, minimal (repeatable)"),
    profile: list[str] = typer.Option(None, "--profile", help="Profiles: minimal, basic, enterprise (repeatable)"),
    dns_ttl: float = typer.Option(None, help="DNS cache TTL (seconds) for resolving"),
):
    presets_final = (preset or []) + edr.expand_profiles(profile or [])
    res = edr.isolate(enable=enable, dry_run=dry_run, block_outbound=block_outbound, allow_hosts=allow_host or [], presets=presets_final, dns_ttl=dns_ttl)
    if res.get("ok") and res.get("dry_run"):
        console.print("[yellow]Dry-run[/]: firewall state change planned")
    elif res.get("ok"):
        console.print("[green]Isolation updated[/]")
    else:
        console.print("[red]Isolation failed[/]")


@app.command()
def triage():
    t = edr.quick_triage_summary()
    table = Table(title="Quick Triage")
    table.add_column("Metric"); table.add_column("Value")
    for k, v in t.items():
        table.add_row(k, str(v))
    console.print(table)


@app.command("scan-file")
def scan_file(path: str):
    data = edr.scan_file(path)
    console.print_json(json.dumps(data))


@app.command("ports")
def list_ports(limit: int = typer.Option(100, help="Max entries to show")):
    ports = edr.list_listening_ports(limit=limit)
    table = Table(title="Listening Ports (EDR)")
    table.add_column("Proto"); table.add_column("Local Address"); table.add_column("PID"); table.add_column("Process")
    for p in ports:
        table.add_row(p.get("proto",""), p.get("laddr",""), str(p.get("pid","")), p.get("proc",""))
    console.print(table)


@app.command("allowlist")
def allowlist(
    allow_host: list[str] = typer.Option(None, "--allow-host", "-a", help="Extra host/IP to include (repeatable)"),
    preset: list[str] = typer.Option(None, "--preset", help="Presets to include: ntp, winupdate, microsoft-basic, m365-core, teams, onedrive, edge-update, minimal (repeatable)"),
    dns_ttl: float = typer.Option(None, help="DNS cache TTL (seconds) for resolving"),
    profile: list[str] = typer.Option(None, "--profile", help="Profiles: minimal, basic, enterprise (repeatable)"),
):
    """Resolve allowlist to IPs (no changes)."""
    presets_final = (preset or []) + edr.expand_profiles(profile or [])
    res = edr.resolve_allowlist(allow_hosts=allow_host or [], presets=presets_final, dns_ttl=dns_ttl)
    console.print_json(json.dumps(res))


@app.command("detect")
def detect(
    rules: str = typer.Option(..., help="Path to rule file (.yml) or directory"),
    limit: int = typer.Option(200, help="Max events to evaluate"),
):
    res = edr.detect(rules_path=rules, limit=limit)
    table = Table(title="EDR Rule Matches")
    table.add_column("Rule"); table.add_column("Matches"); table.add_column("Sample Field")
    for m in res.get("matches", []):
        samp = m.get("sample", {})
        field = (samp.get("Message") or str(list(samp.keys())[:1])) if isinstance(samp, dict) else ""
        table.add_row(m.get("rule",""), str(m.get("count",0)), str(field)[:60])
    console.print(table)


@app.command("quarantine-file")
def quarantine_file(
    path: str,
    dry_run: bool = typer.Option(True, help="Simulate; do not move file"),
    yes: bool = typer.Option(False, help="Skip confirmation when not dry-run"),
):
    if not dry_run and not yes:
        if not typer.confirm(f"Move '{path}' into quarantine? (rollback available)", default=False):
            console.print("[yellow]Aborted by user[/]")
            return
    res = edr.quarantine_file(path, dry_run=dry_run)
    if res.get("dry_run"):
        console.print("[yellow]Dry-run[/]: would quarantine file")
    else:
        console.print("[green]Quarantined[/]")
    console.print_json(json.dumps(res))
@app.command("watch")
def watch(
    rules: str = typer.Option(..., help="Rules file or directory"),
    interval: float = typer.Option(2.0, help="Poll interval (seconds)"),
    sources: str = typer.Option("security,powershell", help="Comma list: security,powershell"),
):
    """Stream new events and evaluate rules until Ctrl-C.

    Note: best-effort polling approach for portability.
    """
    try:
        import time
        from pcsuite.security import logs as _logs
        from pcsuite.security import rules as _rules
    except Exception as e:
        console.print(f"[red]Error loading modules:[/] {e}")
        raise typer.Exit(1)

    ruleset = _rules.load_rules(rules)
    console.print(f"Loaded {len(ruleset)} rule(s) from {rules}")
    last_ids = {"security": 0, "powershell": 0}
    active = {s.strip().lower() for s in (sources or "").split(",")}
    try:
        while True:
            events = []
            if "security" in active:
                evs, last_ids["security"] = _logs.delta_security_events(last_ids["security"])
                events.extend(evs)
            if "powershell" in active:
                evp, last_ids["powershell"] = _logs.delta_powershell_events(last_ids["powershell"])
                events.extend(evp)
            if events:
                matches = _rules.evaluate_events(events, ruleset)
                if matches:
                    table = Table(title=f"EDR Matches ({len(matches)})")
                    table.add_column("Rule"); table.add_column("Matches")
                    for m in matches:
                        table.add_row(str(m.get("rule")), str(m.get("count", 0)))
                    console.print(table)
            time.sleep(max(0.2, float(interval)))
    except KeyboardInterrupt:
        console.print("[yellow]Stopped watching[/]")
agent = typer.Typer(help="Install and manage the background EDR agent (Windows service)")
app.add_typer(agent, name="agent")


def _programdata_agent_dir() -> str:
    return str((Path(os.environ.get("ProgramData") or r"C:\\ProgramData") / "PCSuite" / "agent").resolve())


@agent.command("configure")
def agent_configure(
    rules: str = typer.Option(None, help="Rules file or directory (default: built-in sample rules)"),
    interval: float = typer.Option(2.0, help="Poll interval in seconds"),
    sources: str = typer.Option("security,powershell", help="Comma list of sources"),
    # Auto-response
    auto_response: bool = typer.Option(False, help="Enable auto-response on critical/actions"),
    isolate_block_out: bool = typer.Option(True, help="Auto-response isolation blocks outbound"),
    isolate_preset: list[str] = typer.Option(None, "--isolate-preset", help="Isolation presets (repeatable)"),
    isolate_profile: list[str] = typer.Option(None, "--isolate-profile", help="Isolation profiles: minimal, basic, enterprise (repeatable)"),
    isolate_extra: list[str] = typer.Option(None, "--isolate-extra", help="Isolation extra hosts (repeatable)"),
    isolate_dry_run: bool = typer.Option(True, help="Isolation dry-run when auto-response"),
    isolate_dns_ttl: float = typer.Option(3600.0, help="DNS TTL for isolation allowlist (sec)"),
    # HTTP sink & heartbeat
    sink_url: str = typer.Option(None, help="HTTP sink URL to POST alerts/heartbeats"),
    sink_token: str = typer.Option(None, help="Bearer token for HTTP sink (optional)"),
    sink_verify: bool = typer.Option(True, help="Verify TLS"),
    sink_timeout: float = typer.Option(3.0, help="HTTP timeout (sec)"),
    heartbeat_interval: float = typer.Option(300.0, help="Heartbeat interval seconds (0 to disable)"),
):
    """Write agent config to ProgramData (agent.yml)."""
    import yaml
    base = Path(_programdata_agent_dir())
    base.mkdir(parents=True, exist_ok=True)
    # Expand profiles into presets
    iso_presets = (isolate_preset or []) + edr.expand_profiles(isolate_profile or [])
    cfg = {
        "rules": rules,
        "interval": float(interval),
        "sources": [s.strip() for s in (sources or "").split(",") if s.strip()],
        "auto_response": {
            "enabled": bool(auto_response),
            "isolate": {
                "block_outbound": bool(isolate_block_out),
                "presets": iso_presets,
                "extra_hosts": isolate_extra or [],
                "dry_run": bool(isolate_dry_run),
                "dns_ttl": float(isolate_dns_ttl),
            },
        },
        "http_sink": {
            "url": sink_url,
            "token": sink_token,
            "verify": bool(sink_verify),
            "timeout": float(sink_timeout),
        },
        "heartbeat_interval": float(heartbeat_interval),
    }
    (base / "agent.yml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    console.print(f"[green]Wrote[/] {base / 'agent.yml'}")


def _py_exe() -> str:
    return sys.executable


@agent.command("install")
def agent_install(auto_start: bool = typer.Option(True, help="Set service startup to automatic")):
    """Install the Windows service (requires Administrator)."""
    cmd = f"{_py_exe()} -m pcsuite.agent.service install"
    if auto_start:
        cmd += " --startup auto"
    code, out, err = shell.cmdline(cmd)
    if code == 0:
        console.print("[green]Service installed[/]")
    else:
        console.print(f"[red]Error:[/] {err or out}")


@agent.command("remove")
def agent_remove():
    code, out, err = shell.cmdline(f"{_py_exe()} -m pcsuite.agent.service remove")
    if code == 0:
        console.print("[green]Service removed[/]")
    else:
        console.print(f"[red]Error:[/] {err or out}")


@agent.command("start")
def agent_start():
    code, out, err = shell.cmdline(f"{_py_exe()} -m pcsuite.agent.service start")
    if code == 0:
        console.print("[green]Service started[/]")
    else:
        console.print(f"[red]Error:[/] {err or out}")


@agent.command("stop")
def agent_stop():
    code, out, err = shell.cmdline(f"{_py_exe()} -m pcsuite.agent.service stop")
    if code == 0:
        console.print("[green]Service stopped[/]")
    else:
        console.print(f"[red]Error:[/] {err or out}")


@agent.command("status")
def agent_status():
    # Use sc query for quick state
    code, out, err = shell.cmdline("sc query PCSuiteEDRAgent")
    if code == 0:
        console.print(out)
    else:
        console.print(f"[red]Error:[/] {err or out}")
@app.command("test-generate")
def test_generate(
    source: str = typer.Option("security", help="Source: security|powershell"),
    message: str = typer.Option("DEMO-ISOLATE test event", help="Message to inject"),
):
    ev = seclogs.inject_synthetic_event(source=source, message=message)
    console.print_json(json.dumps({"injected": ev}))
can = typer.Typer(help="Manage canary (decoy) files")
app.add_typer(can, name="canary")

@can.command("generate")
def canary_generate(
    dir: list[str] = typer.Option(..., "--dir", help="Target directory (repeatable)"),
    count: int = typer.Option(1, help="Files per directory"),
):
    res = canary.generate(dir, count_per_dir=count)
    console.print_json(json.dumps(res))

@can.command("list")
def canary_list():
    console.print_json(json.dumps(canary.list_canaries()))

@can.command("clean")
def canary_clean():
    console.print_json(json.dumps(canary.clean()))

@can.command("check")
def canary_check():
    console.print_json(json.dumps(canary.check()))
