from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api import auth, users, inbounds, system, health, subscriptions, stats, xray, admin, qr
from .init_db import init_db

app=FastAPI(title="Railway XPanel",version="1.0.0")
app.include_router(auth.router); app.include_router(users.router); app.include_router(inbounds.router)
app.include_router(system.router); app.include_router(health.router); app.include_router(subscriptions.router)
app.include_router(stats.router); app.include_router(xray.router); app.include_router(admin.router); app.include_router(qr.router)

@app.on_event("startup")
def startup():
    init_db()

static=Path(__file__).parent/"static"
if static.exists():
    app.mount("/assets",StaticFiles(directory=static/"assets"),name="assets")
    @app.get("/{path:path}")
    def frontend(path:str): return FileResponse(static/"index.html")
