"""
FastAPI Server — verbindet alle Komponenten.
Dashboard, Auth, API-Keys, Automationen, Logs, Health-Check.
"""

import os
import secrets
import asyncio
import json
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import DASHBOARD_PASSWORD, ALLOWED_ORIGINS, SESSION_TIMEOUT_HOURS
from backend.database import db
from backend.scheduler import start_scheduler, stop_scheduler, reschedule_automation
from backend.logger import log
from backend import crypto
from backend import rate_limiter
from backend import pipeline


# --- Session-Verwaltung ---

sessions: dict[str, datetime] = {}


def create_session() -> str:
    token = secrets.token_urlsafe(32)
    sessions[token] = datetime.now() + timedelta(hours=SESSION_TIMEOUT_HOURS)
    return token


def verify_session(token: str) -> bool:
    if token not in sessions:
        return False
    if datetime.now() > sessions[token]:
        del sessions[token]
        return False
    return True


async def require_auth(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_session(token):
        raise HTTPException(status_code=401, detail="Nicht autorisiert")


# --- HTTPS-Redirect Middleware ---

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if (
            os.getenv("FORCE_HTTPS", "false").lower() == "true"
            and request.headers.get("x-forwarded-proto") == "http"
        ):
            url = request.url.replace(scheme="https")
            return JSONResponse(
                status_code=307,
                headers={"Location": str(url)},
            )
        return await call_next(request)


# --- App Lifecycle ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init()
    await log("Datenbank initialisiert.")
    await start_scheduler()
    await log("Server gestartet.")
    yield
    await stop_scheduler()
    await db.shutdown()
    await log("Server gestoppt.")


# --- App ---

app = FastAPI(title="Automation Platform", lifespan=lifespan)

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Dashboard (Static File) ---

DASHBOARD_PATH = os.path.join(os.path.dirname(__file__), "..", "dashboard", "index.html")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    if os.path.exists(DASHBOARD_PATH):
        with open(DASHBOARD_PATH, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard nicht gefunden</h1>", status_code=404)


# --- Health ---

@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health():
    db_ok = os.path.exists(db._db_path)
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "ok" if db_ok else "fehlt",
        "timestamp": datetime.now().isoformat(),
    }


# --- Auth ---

@app.post("/api/auth/login")
async def login(request: Request):
    ip = request.client.host

    if not rate_limiter.check_rate_limit(ip):
        raise HTTPException(status_code=429, detail="Zu viele Versuche. Bitte 60 Sekunden warten.")

    body = await request.json()
    password = body.get("password", "")

    if password == DASHBOARD_PASSWORD:
        await rate_limiter.record_attempt(ip, True)
        token = create_session()
        await log(f"Erfolgreicher Login von {ip}.")
        return {"token": token}

    await rate_limiter.record_attempt(ip, False)
    await log(f"Fehlgeschlagener Login von {ip}.", "warning")
    raise HTTPException(status_code=401, detail="Falsches Passwort")


# --- API Keys ---

@app.get("/api/keys", dependencies=[Depends(require_auth)])
async def get_keys():
    return {"keys": crypto.get_masked_keys()}


@app.post("/api/keys", dependencies=[Depends(require_auth)])
async def save_key(request: Request):
    body = await request.json()
    provider = body.get("provider")
    key = body.get("key")
    if not provider or not key:
        raise HTTPException(status_code=400, detail="Provider und Key sind erforderlich.")
    await crypto.save_api_key(provider, key)
    await log(f"API-Key für '{provider}' gespeichert.")
    return {"status": "ok"}


@app.post("/api/keys/test", dependencies=[Depends(require_auth)])
async def test_key(request: Request):
    body = await request.json()
    provider = body.get("provider")
    key = crypto.get_api_key(provider)
    if key is None:
        return {"status": "error", "message": f"Kein Key für '{provider}' gefunden."}
    return {"status": "ok", "message": f"Key für '{provider}' ist vorhanden."}


# --- Automationen ---

@app.get("/api/automations", dependencies=[Depends(require_auth)])
async def get_automations():
    return {"automations": pipeline.get_all_automations()}


@app.post("/api/automations/toggle", dependencies=[Depends(require_auth)])
async def toggle_automation(request: Request):
    body = await request.json()
    name = body.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Name ist erforderlich.")
    new_state = await pipeline.toggle_automation(name)
    reschedule_automation(name, new_state)
    return {"name": name, "enabled": new_state}


@app.get("/api/automations/runs", dependencies=[Depends(require_auth)])
async def get_runs(name: str = None, limit: int = 10):
    return {"runs": db.get_runs(automation_name=name, limit=limit)}


# --- Logs ---

@app.get("/api/logs", dependencies=[Depends(require_auth)])
async def get_logs(limit: int = 100, automation_name: str = None):
    return {"logs": db.get_logs(limit=limit, automation_name=automation_name)}


@app.get("/api/logs/stream", dependencies=[Depends(require_auth)])
async def stream_logs():
    """Server-Sent Events (SSE) für Live-Log-Updates."""
    async def event_generator():
        last_id = 0
        while True:
            logs = db.get_logs(limit=10)
            new_logs = [l for l in logs if l["id"] > last_id]
            for entry in reversed(new_logs):
                last_id = entry["id"]
                data = json.dumps(entry, ensure_ascii=False)
                yield f"data: {data}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# --- Client Config (für Dashboard) ---

@app.get("/api/config", dependencies=[Depends(require_auth)])
async def get_config():
    config = pipeline.get_client_config()
    return {
        "company_name": config.get("company_name", "Automation Platform"),
        "dashboard_title": config.get("dashboard_title", "Dashboard"),
        "api_keys_needed": config.get("api_keys_needed", []),
    }
