# File: app/auth.py
from datetime import datetime, timedelta
from typing import Optional
import os

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "changeme_supersecret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
GITHUB_OAUTH_ENABLED = os.getenv("GITHUB_OAUTH_ENABLED", "false").lower() == "true"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Demo users (for testing)
DEMO_USERS = {
    "admin@example.com": {
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("adminpass"),
        "role": "admin",
        "tenant_id": "tenant_default",
    },
    "viewer@example.com": {
        "email": "viewer@example.com",
        "full_name": "Viewer User",
        "hashed_password": pwd_context.hash("viewerpass"),
        "role": "viewer",
        "tenant_id": "tenant_default",
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    tenant_id: Optional[str] = None


class User(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: str = "viewer"
    tenant_id: str = "tenant_default"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_user(email: str) -> Optional[User]:
    u = DEMO_USERS.get(email)
    if not u:
        return None
    return User(**{k: v for k, v in u.items() if k in ("email", "full_name", "role", "tenant_id")})


def authenticate_user(email: str, password: str) -> Optional[User]:
    user_entry = DEMO_USERS.get(email)
    if not user_entry:
        return None
    if not verify_password(password, user_entry["hashed_password"]):
        return None
    return get_user(email)


# Backwards-compatible: create_access_token(subject=..., role=..., tenant_id=..., expires_delta=...)
def create_access_token(subject: str, role: str = "viewer", tenant_id: str = "tenant_default", expires_delta: Optional[timedelta] = None) -> str:
    """
    Convenience wrapper matching tests' expected signature.
    Encodes a JWT with 'sub', 'role', 'tenant_id' and expiration.
    """
    to_encode = {"sub": subject, "role": role, "tenant_id": tenant_id}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Lower-level variant that accepts a dict payload (kept for backward compat)
def create_access_token_from_dict(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# decode helper used by middleware
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError("Invalid token") from e


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        tenant_id: str = payload.get("tenant_id", "tenant_default")
        if email is None:
            raise credentials_exception
        return User(email=email, role=role, tenant_id=tenant_id)
    except JWTError:
        raise credentials_exception


def require_role(role: str):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role != role and not (role == "viewer" and user.role == "admin"):
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user

    return role_checker


# simple helper to mirror tests
def bearer(token: str) -> str:
    return f"Bearer {token}"


async def github_oauth_stub(request: Request):
    """Returns a stub admin user unless GITHUB_OAUTH_ENABLED is set."""
    if not GITHUB_OAUTH_ENABLED:
        # return a pydantic User instance to be consistent
        return get_user("admin@example.com")
    raise HTTPException(status_code=501, detail="GitHub OAuth not implemented in demo")
