from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
from pcsuite.core import shell


def _signature_status(path: str) -> str:
    # PowerShell Get-AuthenticodeSignature fallback
    # Build command safely without f-string brace ambiguity
    safe = path.replace("'", "''")
    cmd = "try {{ (Get-AuthenticodeSignature -FilePath '{safe}').Status }} catch {{ '' }}".format(
        safe=safe
    )
    code, out, err = shell.pwsh(cmd)
    if code != 0:
        return "unknown"
    val = (out or "").strip()
    return val or "unknown"


def _zone_identifier(path: str) -> dict:
    # Query alternate data stream Zone.Identifier if present (downloaded from internet)
    safe = path.replace("'", "''")
    ps = (
        "try {{"
        "  $s = Get-Item -LiteralPath '{safe}' -Stream Zone.Identifier -ErrorAction SilentlyContinue;"
        "  if($s){{ (Get-Content -LiteralPath $s.PSPath | Out-String) }} else {{ '' }}"
        "}} catch {{ '' }}"
    ).format(safe=safe)
    code, out, err = shell.pwsh(ps)
    if code != 0 or not (out or "").strip():
        return {"has_zone": False, "zone_id": None}
    txt = out.strip()
    # Look for ZoneId=3 etc
    z = None
    for line in txt.splitlines():
        line = line.strip()
        if line.lower().startswith("zoneid="):
            try:
                z = int(line.split("=", 1)[1])
            except Exception:
                z = None
            break
    return {"has_zone": True, "zone_id": z}


def check_reputation(path: str | Path) -> Dict[str, Any]:
    """Best-effort reputation: signature status + Zone.Identifier indicator.

    Returns: { signature: str, has_zone: bool, zone_id: int|None }
    """
    p = str(Path(path))
    sig = _signature_status(p)
    zone = _zone_identifier(p)
    return {"signature": sig, **zone}
