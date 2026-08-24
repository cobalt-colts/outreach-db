import argparse
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
import uvicorn

from app.database import init_db
from app.auth import auth
from app.events import events

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    api = APIRouter(prefix="/api")

    api.include_router(auth)
    api.include_router(events)
    app.include_router(api)
    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reload", action="store_true", help="Enable hot reload")
    args = parser.parse_args()

    uvicorn.run("main:create_app", factory=True, reload=args.reload, host="0.0.0.0")


if __name__ == "__main__":
    main()
