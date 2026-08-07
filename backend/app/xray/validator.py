import subprocess
from ..config import settings

def validate_config():
    p = subprocess.run(
        [settings.XRAY_PATH, "run", "-test", "-config", settings.XRAY_CONFIG],
        capture_output=True, text=True, timeout=20
    )
    return {"success": p.returncode == 0, "output": (p.stdout or "") + (p.stderr or "")}
