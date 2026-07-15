import tomllib

from argon2 import PasswordHasher
from fastapi import FastAPI, APIRouter
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

with open("conf/config.toml", "rb") as file:
    conf = tomllib.load(file)

app = FastAPI()
api = APIRouter(prefix="/api")

app.include_router(api)

app.mount("/_app", StaticFiles(directory="build/_app"), name="_app")

ph = PasswordHasher()

@app.get("/")
async def _root():
    return FileResponse("build/index.html")

@app.get("/{path:path}")
async def _spa():
    return FileResponse("build/index.html")

@api.post("/admin/login/{password}")
def _api_admin_login(
        password: str
):
    try:
        ph.verify(password, conf["admin"]["password"])
