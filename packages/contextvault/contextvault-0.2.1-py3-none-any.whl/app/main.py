# File: app/main.py
from __future__ import annotations
from datetime import timedelta
import os  # <--- added

from fastapi import FastAPI, Request, Query, HTTPException, status, Depends
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.api.health import router as health_router
from app.core.scheduler import RetentionScheduler, ENABLED as RETENTION_ENABLED, DEFAULT_INTERVAL
from app.core.retention import cleanup_expired

# Legacy router (your existing endpoints)
from app.api.routes import router as legacy_router
from app.api.p2_admin import router as p2_admin_router
from app.api.p3_search import router as p3_search_router
# ensure GET /relationships is always available (for compatibility)
from app.core.storage.filelog import iter_events
from app.api.p1_index_worker import router as p1_index_worker_router
from app.api.p1_metrics import router as p1_metrics_router
from app.api.p1_search import router as p1_search_router

# New additive routers
from app.api.p0_routes import router as p0_router
from app.api.p1_routes import router as p1_router
from app.api.p3_routes import router as p3_router
from app.api.p2_embeddings import router as embeddings_router
from app.api.p1_dag import router as p1_dag_router

# Auth helpers (from the auth module)
from app import auth

app = FastAPI(
    title="ContextVault",
    version="1.2.0",
    description="ContextVault API (RBAC + Encryption + Indexing + SaaS-Readiness)",
)

_scheduler = None
if RETENTION_ENABLED:
    try:
        interval = int(os.environ.get("RETENTION_INTERVAL_SECONDS", str(DEFAULT_INTERVAL)))
    except Exception:
        interval = DEFAULT_INTERVAL
    _scheduler = RetentionScheduler(cleanup_expired, interval)
    
@app.on_event("startup")
async def startup_event():
    # start retention scheduler
    if _scheduler:
        _scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    if _scheduler:
        _scheduler.stop()    

# Mount routers — legacy first to preserve semantics
app.include_router(legacy_router)
app.include_router(p0_router)
app.include_router(p1_router)
app.include_router(p3_router)
app.include_router(embeddings_router)
app.include_router(p1_dag_router)
app.include_router(p2_admin_router)
app.include_router(p3_search_router)
app.include_router(p1_index_worker_router)
app.include_router(p1_metrics_router)
app.include_router(p1_search_router)
app.include_router(health_router)


@app.get("/_routes")
def list_routes():
    return [{"path": r.path, "methods": list(r.methods)} for r in app.routes if isinstance(r, APIRoute)]


@app.get("/")
def health():
    return {"status": "ok", "version": app.version}


@app.get("/relationships")
def _relationships_get(node_type: str = Query(..., pattern="^(object|context)$"), node_id: str = Query(...)):
    out: list[dict] = []
    for ev in iter_events("relationships") or []:
        f = ev.get("from", {})
        t = ev.get("to", {})
        if (f.get("type") == node_type and f.get("id") == node_id) or (t.get("type") == node_type and t.get("id") == node_id):
            out.append(ev)
    return {"type": node_type, "id": node_id, "relationships": out}


# ------------------------
# Authentication endpoints
# ------------------------
@app.post("/auth/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Exchange username/password for JWT access token.
    """
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(subject=user.email, role=user.role, tenant_id=user.tenant_id, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/github")
async def github_auth(request: Request):
    """
    Minimal GitHub OAuth stub.
    """
    user = await auth.github_oauth_stub(request)
    if not user:
        raise HTTPException(status_code=500, detail="OAuth failed")
    access_token = auth.create_access_token(subject=user.email, role=user.role, tenant_id=user.tenant_id)
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------
# Lightweight UI protection middleware
# ------------------------
@app.middleware("http")
async def ui_protection_middleware(request: Request, call_next):
    path = request.url.path or ""
    protect_prefixes = ("/ui", "/api/ui")
    admin_prefixes = ("/ui/admin", "/api/ui/admin")

    # Only enforce for UI-prefixed routes
    if any(path.startswith(p) for p in protect_prefixes):
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Missing or invalid Authorization header"})
        token = auth_header.split(" ", 1)[1].strip()

        # decode token (use helper from auth module)
        try:
            payload = auth.decode_access_token(token)
        except Exception as e:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid token", "error": str(e)})

        role = payload.get("role")
        # admin-specific enforcement: paths under /ui/admin or /api/ui/admin require admin role strictly
        if any(path.startswith(p) for p in admin_prefixes):
            if role != "admin":
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Admin role required"})
        else:
            # For other UI paths, allow viewer or admin
            if role not in ("viewer", "admin"):
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Insufficient role"})

        # attach payload to request.state for downstream use
        request.state.token_payload = payload

    return await call_next(request)


# ------------------------
# Minimal UI test route (protected by middleware)
# ------------------------
@app.get("/ui/test")
async def ui_test(request: Request):
    payload = getattr(request.state, "token_payload", None)
    return {"ok": True, "user": payload}


# ------------------------
# Protected route used by tests (deterministic)
# ------------------------
@app.get("/api/ui/data")
async def api_ui_data(request: Request):
    """
    Minimal protected endpoint for UI clients. Tests call /api/ui/data after obtaining a token.
    This exists to make token-based UI access deterministic: it returns 200 when token is valid.
    """
    payload = getattr(request.state, "token_payload", None)
    return {"ok": True, "user": payload}


# ------------------------
# Generic exception handler
# ------------------------
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=500, content={"detail": str(exc)})
