# app/api/admin_audit.py
from fastapi import APIRouter, Request, HTTPException, Query, Response
from typing import Any
from app.core.audit_log import get_audit
from app import auth

router = APIRouter(prefix="/admin", tags=["admin"])

def _require_admin(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization")
    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = auth.decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return payload

@router.get("/audit/tail")
def audit_tail(request: Request, lines: int = Query(100, ge=1, le=1000)):
    _require_admin(request)
    audit = get_audit()
    out = audit.tail(lines)
    return {"lines": len(out), "entries": out}

@router.get("/audit/export")
def audit_export(request: Request):
    _require_admin(request)
    audit = get_audit()
    p = audit.path if hasattr(audit, "path") else None
    if p and p.exists():
        # stream the file contents as application/jsonl
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            data = f.read()
        return Response(content=data, media_type="application/json")
    else:
        return {"error": "audit file not found"}
