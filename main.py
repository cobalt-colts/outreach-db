from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.database import apply_sql_folder
from app.auth import auth


PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"


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
