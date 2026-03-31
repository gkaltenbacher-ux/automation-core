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
from backend.credentials import create_credential_manager, create_get_api_key
from backend.dsgvo import create_dsgvo_manager
from backend.cost_tracker import CostTracker
from backend.orchestrator import Orchestrator
from tools import load_tool_registry
from agents import load_agent_registry
from backend.workflow_engine import WorkflowEngine


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


# --- Credential Manager ---

_client_config = pipeline.get_client_config()
_data_dir = str(db._db_path).replace("database.db", "")
credential_manager = create_credential_manager(_client_config, data_dir=_data_dir)
get_api_key = create_get_api_key(credential_manager)
dsgvo_manager = create_dsgvo_manager(_client_config, data_dir=_data_dir)
cost_tracker = CostTracker(data_dir=_data_dir)

# --- Tool + Agent Registry ---
_tool_registry = load_tool_registry()
_agent_context = {
    "get_api_key": get_api_key,
    "log": log,
    "db": db,
    "dsgvo": dsgvo_manager,
    "cost_tracker": cost_tracker,
}
_agent_registry = load_agent_registry(
    tool_registry=_tool_registry,
    config=_client_config,
    context=_agent_context,
)

# --- Orchestrator ---
_orch_config = _client_config.get("orchestrator", {})
orchestrator = Orchestrator(
    credential_manager=credential_manager,
    agent_registry=_agent_registry,
    config=_orch_config,
    cost_tracker=cost_tracker,
) if _orch_config.get("enabled", False) else None

# --- Workflow Engine ---
workflow_engine = WorkflowEngine(
    agent_registry=_agent_registry,
    tool_registry=_tool_registry,
    context=_agent_context,
    data_dir=_data_dir,
)


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


# --- Credentials (neues System) ---

@app.get("/api/credentials/types", dependencies=[Depends(require_auth)])
async def get_credential_types():
    return {"types": credential_manager.get_credential_types()}


@app.get("/api/credentials", dependencies=[Depends(require_auth)])
async def list_credentials():
    return {"credentials": credential_manager.list_all()}


@app.post("/api/credentials", dependencies=[Depends(require_auth)])
async def save_credential(request: Request):
    body = await request.json()
    cred_type = body.get("type")
    name = body.get("name", cred_type)
    data = body.get("data", {})
    cred_id = body.get("id")

    if not cred_type or not data:
        raise HTTPException(status_code=400, detail="Typ und Daten sind erforderlich.")

    if cred_id:
        credential_manager.update(cred_id, data)
        await log(f"Credential '{name}' aktualisiert.")
        return {"status": "ok", "id": cred_id}

    new_id = credential_manager.create(name, cred_type, data)
    await log(f"Credential '{name}' gespeichert.")
    return {"status": "ok", "id": new_id}


@app.post("/api/credentials/test", dependencies=[Depends(require_auth)])
async def test_credential(request: Request):
    body = await request.json()
    cred_id = body.get("id")
    if not cred_id:
        raise HTTPException(status_code=400, detail="Credential-ID erforderlich.")
    result = await credential_manager.test(cred_id)
    return result


@app.delete("/api/credentials/{cred_id}", dependencies=[Depends(require_auth)])
async def delete_credential(cred_id: str):
    credential_manager.delete(cred_id)
    await log(f"Credential '{cred_id}' geloescht.")
    return {"status": "ok"}


# --- DSGVO ---

@app.get("/api/dsgvo/persons", dependencies=[Depends(require_auth)])
async def dsgvo_list_persons(limit: int = 100):
    if not dsgvo_manager:
        raise HTTPException(status_code=404, detail="DSGVO-Modul nicht aktiviert")
    return {"persons": await dsgvo_manager.list_persons(limit)}


@app.get("/api/dsgvo/persons/{person_id:path}", dependencies=[Depends(require_auth)])
async def dsgvo_export_person(person_id: str):
    if not dsgvo_manager:
        raise HTTPException(status_code=404, detail="DSGVO-Modul nicht aktiviert")
    return await dsgvo_manager.export_person_data(person_id)


@app.delete("/api/dsgvo/persons/{person_id:path}", dependencies=[Depends(require_auth)])
async def dsgvo_delete_person(person_id: str):
    if not dsgvo_manager:
        raise HTTPException(status_code=404, detail="DSGVO-Modul nicht aktiviert")
    result = await dsgvo_manager.delete_person_data(person_id)
    await log(f"DSGVO: Daten fuer '{person_id}' geloescht.")
    return result


@app.get("/api/dsgvo/consents", dependencies=[Depends(require_auth)])
async def dsgvo_list_consents(person_id: str = None):
    if not dsgvo_manager:
        raise HTTPException(status_code=404, detail="DSGVO-Modul nicht aktiviert")
    return {"consents": await dsgvo_manager.get_consents(person_id)}


@app.post("/api/dsgvo/consents", dependencies=[Depends(require_auth)])
async def dsgvo_add_consent(request: Request):
    if not dsgvo_manager:
        raise HTTPException(status_code=404, detail="DSGVO-Modul nicht aktiviert")
    body = await request.json()
    await dsgvo_manager.log_consent(
        person_id=body["person_id"],
        category=body["category"],
        purpose=body["purpose"],
        source=body.get("source", "manual"),
        consent_type=body.get("consent_type", "legitimate_interest"),
        notes=body.get("notes"),
    )
    return {"status": "ok"}


@app.delete("/api/dsgvo/consents/{person_id:path}", dependencies=[Depends(require_auth)])
async def dsgvo_revoke_consent(person_id: str, category: str = None):
    if not dsgvo_manager:
        raise HTTPException(status_code=404, detail="DSGVO-Modul nicht aktiviert")
    await dsgvo_manager.revoke_consent(person_id, category)
    return {"status": "ok"}


@app.get("/api/dsgvo/audit", dependencies=[Depends(require_auth)])
async def dsgvo_audit_trail(person_id: str = None, limit: int = 100):
    if not dsgvo_manager:
        raise HTTPException(status_code=404, detail="DSGVO-Modul nicht aktiviert")
    return {"audit": await dsgvo_manager.get_audit_trail(person_id, limit)}


# --- Kosten ---

@app.get("/api/costs/summary", dependencies=[Depends(require_auth)])
async def costs_summary(period: str = "today"):
    return cost_tracker.get_summary(period)


# --- Chat (Orchestrator) ---

@app.post("/api/chat", dependencies=[Depends(require_auth)])
async def chat_with_orchestrator(request: Request):
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Orchestrator nicht aktiviert")
    body = await request.json()
    message = body.get("message", "")
    user_id = body.get("user_id", "dashboard")
    if not message:
        raise HTTPException(status_code=400, detail="Nachricht fehlt")
    response = await orchestrator.chat(message, user_id)
    return {"response": response}


# --- Agents ---

@app.get("/api/agents", dependencies=[Depends(require_auth)])
async def list_agents():
    agents_info = []
    for name, agent in _agent_registry.items():
        agents_info.append({
            "name": name,
            "role": agent.role,
            "description": agent.description,
            "tools": agent.tools,
            "model": agent.model,
            "enabled": True,
        })
    return {"agents": agents_info}


# --- Workflows ---

@app.get("/api/workflows", dependencies=[Depends(require_auth)])
async def list_workflow_definitions():
    return {"workflows": _client_config.get("workflows", [])}


@app.get("/api/workflows/runs", dependencies=[Depends(require_auth)])
async def list_workflow_runs(workflow_name: str = None, limit: int = 20):
    return {"runs": workflow_engine.list_runs(workflow_name, limit)}


@app.get("/api/workflows/runs/{run_id}", dependencies=[Depends(require_auth)])
async def get_workflow_run(run_id: str):
    status = workflow_engine.get_status(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow-Run nicht gefunden")
    return status


@app.post("/api/workflows/{workflow_name}/start", dependencies=[Depends(require_auth)])
async def start_workflow(workflow_name: str, request: Request):
    workflows = _client_config.get("workflows", [])
    workflow_def = next((w for w in workflows if w["name"] == workflow_name), None)
    if not workflow_def:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' nicht gefunden")
    body = await request.json() if await request.body() else {}
    run_id = await workflow_engine.start(workflow_def, initial_data=body.get("data"))
    return {"run_id": run_id, "status": "gestartet"}


@app.post("/api/workflows/runs/{run_id}/resume", dependencies=[Depends(require_auth)])
async def resume_workflow(run_id: str):
    status = workflow_engine.get_status(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow-Run nicht gefunden")
    workflow_name = status["workflow_name"]
    workflows = _client_config.get("workflows", [])
    workflow_def = next((w for w in workflows if w["name"] == workflow_name), None)
    if not workflow_def:
        raise HTTPException(status_code=404, detail=f"Workflow-Definition '{workflow_name}' nicht gefunden")
    result = await workflow_engine.resume(run_id, workflow_def)
    return {"status": result}
