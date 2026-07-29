import datetime
import os
import sqlite3
import tomllib
from http.client import HTTPException
from time import timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.responses import JSONResponse

from app.database import get_user_from_email, PROJECT_ROOT
from app.models import LoginModel

auth = APIRouter(prefix="/api/auth")

bearer = HTTPBearer()
ph = PasswordHasher()

def _project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path

def _load_jwt_key(environment_name: str, default_path: Path) -> str:
    configured_path = os.getenv(environment_name)
    key_path = _project_path(configured_path) if configured_path else default_path
    try:
        return key_path.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError(
            f"Unable to load {environment_name} from {key_path}. "
            f"Set {environment_name} to a readable key file."
        ) from error


with (PROJECT_ROOT / "conf" / "config.toml").open("rb") as file:
    conf = tomllib.load(file)

jwt_ssh_dir = _project_path(os.getenv("JWT_SSH_DIR", "~/.ssh"))
RSA_PRIVATE_KEY = _load_jwt_key(
    "JWT_PRIVATE_KEY_PATH", jwt_ssh_dir / "id_rsa_jwt"
)
RSA_PUBLIC_KEY = _load_jwt_key(
    "JWT_PUBLIC_KEY_PATH", jwt_ssh_dir / "id_rsa_jwt.pub"
)


async def get_auth_payload(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "missing or invalid authorization")

    try:
        payload = jwt.decode(
            credentials.credentials,
            RSA_PUBLIC_KEY,
            algorithms=["RS256"],
            options={"require": ["exp", "uid", "permissions"]},
        )
    except jwt.InvalidTokenError as error:
        raise HTTPException(401, "invalid or expired token") from error

    uid = payload.get("uid")
    if isinstance(uid, bool) or not isinstance(uid, int):
        raise HTTPException(401, "invalid token payload")

    return payload

@auth.get
async def _api_login(body: LoginModel):
    try:
        user = get_user_from_email(body.email)
    except sqlite3.Error as e:
        raise HTTPException(403, "User not found")

    try:
        ph.verify(body.password, user['password'])
    except Exception:
        raise HTTPException(403, "Incorrect password")

    authtoken = jwt.encode(
        {
            "id": user["id"],
            "permissions": user["permission_level"],
            "exp": int((datetime.now(timezone.utc) + datetime.timedelta(hours=24)).timestamp()),
        },
        RSA_PRIVATE_KEY,
        algorithm="RS256",
    )

    return JSONResponse({"auth_token": authtoken})

