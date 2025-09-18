# File: app/middleware/rbac.py
"""
RBAC middleware enforcing access control on /ui/* routes.

Rules:
- Unauthenticated requests to /ui/* -> 401
- Authenticated requests with role 'viewer' or 'admin' allowed by default.
- Route-specific restrictions can be added by checking request.method/path.
- Example: a write route under /ui/admin/* could be restricted to role 'admin'.

This middleware uses the app.auth.decode_access_token function to validate tokens.
"""

from __future__ import annotations
from typing import Callable, Awaitable
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import JSONResponse
from starlette.datastructures import Headers

from app.auth import decode_access_token
import logging

log = logging.getLogger("contextvault.rbac")


def _extract_bearer_from_headers(headers: Headers) -> str | None:
    auth = headers.get("authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


class RBACMiddleware:
    def __init__(self, app: ASGIApp, ui_prefix: str = "/ui"):
        self.app = app
        self.ui_prefix = ui_prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Only enforce for http requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        # Only enforce on /ui prefixed routes
        if not path.startswith(self.ui_prefix):
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        token = _extract_bearer_from_headers(headers)
        if not token:
            res = JSONResponse({"detail": "Missing authentication token"}, status_code=401)
            await res(scope, receive, send)
            return

        try:
            payload = decode_access_token(token)
        except Exception as e:
            log.debug("token decode failed: %s", e)
            res = JSONResponse({"detail": f"Invalid token: {e}"}, status_code=401)
            await res(scope, receive, send)
            return

        # Attach user info into scope for downstream routes if required
        scope.setdefault("ctxvault", {})
        scope["ctxvault"]["user"] = {"sub": payload.get("sub"), "role": payload.get("role")}

        # Example role check: if path contains '/admin' require admin role
        if "/admin" in path:
            role = payload.get("role")
            if role != "admin":
                res = JSONResponse({"detail": "Insufficient role for this resource (admin required)"}, status_code=403)
                await res(scope, receive, send)
                return

        # allowed
        await self.app(scope, receive, send)
