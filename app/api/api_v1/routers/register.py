from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.constants import UserRoleEnum
from app.core.config import settings
from app.core import security
from fastapi import APIRouter, Depends, Response, HTTPException, status, Form
from fastapi.encoders import jsonable_encoder


router = APIRouter(
    prefix="/register",
    tags=["register"]
)


@router.post(
    path="",
    # response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(deps.disabled_endpoint)]
)
async def register_user(
    response: Response,
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(deps.get_async_db),
) -> Any:
    """
    Create new user.
    """
    if await crud.user.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this email already exists in the system"
        )

    if await crud.user.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists in the system"
        )
    user_in = jsonable_encoder(user_in)
    user_in = schemas.UserCreateInDB(**user_in, role=UserRoleEnum.USER)

    user = await crud.user.create(db, obj_in=user_in)

    # Login user when registered
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = security.create_access_token(
        user=user,
        expires_delta=access_token_expires
    )

    response.set_cookie(key="access_token", value=token, httponly=True, secure=True, max_age=int(access_token_expires.total_seconds()))

    return {"message": "Successfully registered"}
