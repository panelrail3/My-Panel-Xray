import json, secrets, subprocess
from pathlib import Path
from ..config import settings

STATE = Path(settings.XRAY_CONFIG).parent / "reality.json"

def _parse_keypair(text: str):
    private = public = ""
    for line in text.splitlines():
        low = line.lower().strip()
        if low.startswith("private key:"):
            private = line.split(":", 1)[1].strip()
        elif low.startswith("public key:"):
            public = line.split(":", 1)[1].strip()
    if not private or not public:
        raise RuntimeError("Unable to parse Xray x25519 keypair output")
    return private, public

def ensure_reality_keypair():
    if settings.REALITY_PRIVATE_KEY and settings.REALITY_PUBLIC_KEY:
        return settings.REALITY_PRIVATE_KEY, settings.REALITY_PUBLIC_KEY

    STATE.parent.mkdir(parents=True, exist_ok=True)
    if STATE.exists():
        try:
            data=json.loads(STATE.read_text())
            if data.get("privateKey") and data.get("publicKey"):
                return data["privateKey"], data["publicKey"]
        except Exception:
            pass

    p=subprocess.run(
        [settings.XRAY_PATH, "x25519"],
        capture_output=True, text=True, timeout=10
    )
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or "xray x25519 failed").strip())

    private, public = _parse_keypair((p.stdout or "") + (p.stderr or ""))
    STATE.write_text(json.dumps({
        "privateKey": private,
        "publicKey": public,
    }, indent=2))
    return private, public

def reality_parameters():
    private, public = ensure_reality_keypair()
    short_id = settings.REALITY_SHORT_ID or secrets.token_hex(8)
    server_name = settings.REALITY_SERVER_NAME or "www.microsoft.com"
    target = server_name if ":" in server_name else f"{server_name}:443"
    return {
        "privateKey": private,
        "publicKey": public,
        "shortId": short_id,
        "serverName": server_name,
        "target": target,
    }
