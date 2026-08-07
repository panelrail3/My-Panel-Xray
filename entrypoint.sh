#!/bin/sh
set -eu
mkdir -p /data/xray /data/xray/backups
python -m backend.app.init_db
python - <<'PY'
from backend.app.database import SessionLocal
from backend.app.models import User, Inbound
from backend.app.xray.generator import build_config, write_atomic
from backend.app.config import settings
db=SessionLocal()
try:
    write_atomic(build_config(db.query(Inbound).all(),db.query(User).all()),settings.XRAY_CONFIG)
finally: db.close()
PY
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
