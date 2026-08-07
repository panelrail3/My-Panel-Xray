import subprocess
from pathlib import Path
from ..config import settings
from .validator import validate_config

class XrayManager:
    def __init__(self): self.process=None
    def available(self): return Path(settings.XRAY_PATH).exists()
    def start(self):
        if not self.available(): return {"status":"unavailable"}
        if self.process and self.process.poll() is None: return {"status":"running","pid":self.process.pid}
        self.process=subprocess.Popen([settings.XRAY_PATH,"run","-config",settings.XRAY_CONFIG],
                                      stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
        return {"status":"running","pid":self.process.pid}
    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=10)
            except subprocess.TimeoutExpired: self.process.kill()
        return {"status":"stopped"}
    def restart(self):
        self.stop(); return self.start()
    def status(self):
        if self.process and self.process.poll() is None: return {"status":"running","pid":self.process.pid}
        return {"status":"stopped"}
manager=XrayManager()
