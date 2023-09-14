from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.api_v1.api import router
from app.core.config import settings
from app.core.ssh_tunnel import ssh_tunnel_manager
from app.static_files import PATH_STATIC_FILES

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

origins = [
    "https://192.168.1.4:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_STR)

app.mount("/static", StaticFiles(directory=PATH_STATIC_FILES), name="static")


@app.get("/health")
async def root():
    return {"message": "ok"}


@app.on_event("startup")
async def startup_event():
    if settings.ENVIRONMENT == "prod":
        ssh_tunnel_manager.start_tunnel()


@app.on_event("shutdown")
async def shutdown_event():
    if settings.ENVIRONMENT == "prod":
        ssh_tunnel_manager.stop_tunnel()