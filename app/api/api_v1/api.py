from app.api.api_v1.routers import users, profiles, login, register
from fastapi import APIRouter


router = APIRouter()

router.include_router(users.router)
router.include_router(profiles.router)
router.include_router(login.router)
router.include_router(register.router)
