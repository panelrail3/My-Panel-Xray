#!/bin/sh
set -eu
mkdir -p /data/xray /data/xray/backups
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
