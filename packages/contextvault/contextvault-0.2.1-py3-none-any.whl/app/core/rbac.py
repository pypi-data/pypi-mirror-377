# app/core/rbac.py
"""
Minimal RBAC stub.

API:
  - add_user_role(user: str, role: str) -> None
  - remove_user_role(user: str, role: str) -> None
  - check_permission(user: str, action: str) -> bool
  - get_roles(user: str) -> List[str]
  - list_users() -> Dict[str, List[str]]

Behavior:
- In-memory only (process-lifetime).
- Default permissions mapping provided for convenience.
- Safe and deterministic for tests. No persistent storage.
"""

from __future__ import annotations
import threading
from typing import Dict, List

_lock = threading.RLock()

# user -> [roles...]
_roles: Dict[str, List[str]] = {}

# role -> [allowed_actions...]
_permissions: Dict[str, List[str]] = {
    "admin": ["ingest", "search", "manage", "retention"],
    "ingestor": ["ingest"],
    "reader": ["search"],
    "ops": ["manage", "retention"],
}


def add_user_role(user: str, role: str) -> None:
    """Grant `role` to `user` (idempotent)."""
    if not user or not role:
        return
    with _lock:
        lst = _roles.setdefault(user, [])
        if role not in lst:
            lst.append(role)


def remove_user_role(user: str, role: str) -> None:
    """Revoke `role` from `user` (if present)."""
    if not user or not role:
        return
    with _lock:
        if user in _roles and role in _roles[user]:
            _roles[user].remove(role)
            if not _roles[user]:
                del _roles[user]


def check_permission(user: str, action: str) -> bool:
    """
    Return True if the user has any role that allows `action`.
    Example actions: 'ingest', 'search', 'manage', 'retention'
    """
    if not user or not action:
        return False
    with _lock:
        roles = _roles.get(user, [])
        for r in roles:
            perms = _permissions.get(r, [])
            if action in perms:
                return True
    return False


def get_roles(user: str) -> List[str]:
    """Return list of roles assigned to user (copy)."""
    with _lock:
        return list(_roles.get(user, []))


def list_users() -> Dict[str, List[str]]:
    """Return a shallow copy of the user->roles mapping."""
    with _lock:
        return {u: list(rlist) for u, rlist in _roles.items()}


# Small convenience: seed a default admin for local dev if not present
def _seed_dev_admin():
    with _lock:
        if "admin" not in list_users().get("dev-admin", []):
            add_user_role("dev-admin", "admin")

# seed at import (harmless)
_seed_dev_admin()
