import time
from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas, models
from app.api import deps
from app.constants import UserRoleEnum
from app.schemas.base import ResponseWithPagination

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
    # dependencies=[Depends(deps.require_admin)]
)


@router.get(
    path="/{username}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ResponseProfile
)
async def read_profile(
    username: str,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Retrieve all users
    """
    db_user = await crud.user.get_by_username(db, username=username, including=[models.Tile])
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user not found"
        )
    return db_user


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ResponseProfile
)
async def read_current_user_profile(
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Retrieve current user profile
    """
    profile = await crud.user.get(db, id=current_user.id, including=[models.Tile])
    return profile


@router.post(
    path="/tile",
    status_code=status.HTTP_200_OK,
    # response_model=
)
async def create_tile_for_current_profile(
    tile_in: schemas.TileCreate,
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    """

    # await crud.tile.create(db, obj_in=)


@router.post(
    path="/short-link/get-or-create",
    status_code=status.HTTP_200_OK,
    # response_model=
)
async def get_or_create_tile_short_link(
    short_id: str,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    """
    ...


