import os
import tomllib
from contextlib import asynccontextmanager
from functools import wraps
from inspect import isawaitable
from pathlib import Path
from typing import Any

import argon2
import jwt
from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.database import apply_sql_folder, get_me


PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"


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


@asynccontextmanager
async def lifespan(_: FastAPI):
    apply_sql_folder()
    yield


app = FastAPI(lifespan=lifespan)
api = APIRouter(prefix="/api")
ph = PasswordHasher()
bearer = HTTPBearer(auto_error=False)


class AdminLogin(BaseModel):
    password: str


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


PERMISSION_ERROR = "You don't have the correct permissions to perform this action."


def permission_required(permission_level: int | tuple[int, ...]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            payload = kwargs.get("payload")
            if not isinstance(payload, dict):
                raise HTTPException(401, "invalid token payload")

            uid = payload.get("uid")
            if isinstance(uid, bool) or not isinstance(uid, int):
                raise HTTPException(401, "invalid token payload")

            user = get_me(uid)
            if user is None:
                raise HTTPException(401, "invalid token payload")

            allowed_levels = (
                permission_level
                if isinstance(permission_level, tuple)
                else (permission_level,)
            )
            if user["permission_level"] not in allowed_levels:
                raise HTTPException(status_code=403, detail=PERMISSION_ERROR)

            response = func(*args, **kwargs)
            return await response if isawaitable(response) else response

        return wrapper

    return decorator


@api.post("/admin/login")
async def _api_admin_login(login: AdminLogin) -> dict[str, bool]:
    try:
        ph.verify(conf["admin"]["ADMIN_PASSWORD_HASH"], login.password)
    except argon2.exceptions.VerificationError as error:
        raise HTTPException(status_code=401, detail="Incorrect password") from error

    return {"authenticated": True}


app.include_router(api)
app.mount(
    "/_app",
    StaticFiles(directory=BUILD_DIR / "_app", check_dir=False),
    name="_app",
)


def _frontend_index() -> FileResponse:
    index_file = BUILD_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(503, "Frontend build missing; run `bun run build`.")
    return FileResponse(index_file)


@app.get("/")
async def _root():
    return _frontend_index()


@app.get("/{path:path}")
async def _spa():
    return _frontend_index()
