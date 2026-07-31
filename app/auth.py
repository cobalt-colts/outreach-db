from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any

import argon2
import jwt
from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import PROJECT_ROOT, get_user, get_user_from_email, update_password_hash
from app.models import CurrentUserResponse, LoginModel, TokenResponse


JWT_ALGORITHM = "RS256"
TOKEN_LIFETIME = timedelta(hours=24)
auth = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)
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


jwt_ssh_dir = _project_path(os.getenv("JWT_SSH_DIR", "~/.ssh"))
RSA_PRIVATE_KEY = _load_jwt_key("JWT_PRIVATE_KEY_PATH", jwt_ssh_dir / "id_rsa_jwt")
RSA_PUBLIC_KEY = _load_jwt_key("JWT_PUBLIC_KEY_PATH", jwt_ssh_dir / "id_rsa_jwt.pub")


def _unauthorized(detail: str = "invalid email or password") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_auth_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("missing or invalid authorization")

    try:
        payload = jwt.decode(
            credentials.credentials,
            RSA_PUBLIC_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "uid", "permissions"]},
        )
    except jwt.InvalidTokenError as error:
        raise _unauthorized("invalid or expired token") from error

    uid = payload.get("uid")
    permissions = payload.get("permissions")
    if (
        isinstance(uid, bool)
        or not isinstance(uid, int)
        or isinstance(permissions, bool)
        or not isinstance(permissions, int)
    ):
        raise _unauthorized("invalid token payload")

    user = get_user(uid)
    if user is None or user["permission_level"] != permissions:
        raise _unauthorized("invalid token payload")

    return payload


@auth.post("/login", response_model=TokenResponse)
async def login(body: LoginModel) -> TokenResponse:
    email = body.email.strip().lower()
    user = get_user_from_email(email)
    if user is None:
        raise _unauthorized()

    try:
        ph.verify(user["password_argon2"], body.password)
    except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHashError) as error:
        raise _unauthorized() from error

    if ph.check_needs_rehash(user["password_argon2"]):
        update_password_hash(user["id"], ph.hash(body.password))

    issued_at = datetime.now(timezone.utc)
    access_token = jwt.encode(
        {
            "uid": user["id"],
            "permissions": user["permission_level"],
            "iat": issued_at,
            "exp": issued_at + TOKEN_LIFETIME,
        },
        RSA_PRIVATE_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return TokenResponse(access_token=access_token)


@auth.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    payload: dict[str, Any] = Depends(get_auth_payload),
) -> CurrentUserResponse:
    user = get_user(payload["uid"])
    if user is None:
        raise _unauthorized("invalid token payload")
    return CurrentUserResponse(
        id=user["id"],
        email=user["email"],
        permission_level=user["permission_level"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        team_number=user["team_number"]
    )
