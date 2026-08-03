import argparse
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
import uvicorn

from app.database import init_db
from app.auth import auth
from app.events import events

PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def _frontend_index() -> FileResponse:
    index_file = BUILD_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(503, "Frontend build missing; run `bun run build`.")
    return FileResponse(index_file)


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    api = APIRouter(prefix="/api")

    api.include_router(auth)
    api.include_router(events)
    app.include_router(api)
    app.mount(
        "/_app",
        StaticFiles(directory=BUILD_DIR / "_app", check_dir=False),
        name="_app",
    )

    @app.get("/")
    async def _root():
        return _frontend_index()

    @app.get("/{path:path}")
    async def _spa():
        return _frontend_index()

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reload", action="store_true", help="Enable hot reload")
    args = parser.parse_args()

    uvicorn.run("main:create_app", factory=True, reload=args.reload, host="0.0.0.0")


if __name__ == "__main__":
    main()
