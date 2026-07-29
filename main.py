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

from app.database import apply_sql_folder, get_user
from app.auth import auth


PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"


def _project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


@asynccontextmanager
async def lifespan(_: FastAPI):
    apply_sql_folder()
    yield


app = FastAPI(lifespan=lifespan)
api = APIRouter(prefix="/api")

api.include_router(auth)

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
