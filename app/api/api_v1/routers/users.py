import time
from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas, models
from app.api import deps
from app.constants import UserRoleEnum
from app.core.security import verify_password
from app.schemas.base import ResponseWithPagination
from app.static_files import PATH_STATIC_FILES
from app.utils.func import UserPictureManager as user_picture_manager

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(deps.require_admin)]
)


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=ResponseWithPagination[schemas.UserSimple]
)
async def read_users(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Retrieve all users
    """
    offset = (page - 1) * page_size
    db_users, total_count = await crud.user.get_multi(db, offset=offset, limit=page_size)
    total_pages = 1 + total_count//page_size
    return {"items": db_users, "total_count": total_count, "total_pages": total_pages}


@router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSimple
)
async def read_user(
    user_id: UUID4,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Retrieve a user by it's ID.
    """
    db_user = crud.user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return db_user


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserSimple,
    dependencies=[Depends(deps.require_admin)]
)
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Create a new user
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

    db_user = await crud.user.create(db, obj_in=user_in)
    return db_user


@router.patch(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSimple
)
async def update_user(
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Update the current user
    """
    if (
        user_in.email is not None
        and crud.user.get_by_email(db, email=user_in.email)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The email is already used"
        )
    if (
        user_in.username is not None
        and crud.user.get_by_username(db, username=user_in.username)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The username is already used"
        )
    return await crud.user.update(db, db_obj=current_user, obj_in=user_in)


@router.patch(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSimple,
    dependencies=[Depends(deps.require_admin)]
)
async def update_user_by_id(
    user_id: UUID4,
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Update the current user
    """
    db_user = await crud.user.get(db, id=user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID no exists on the system"
        )

    if (
        user_in.email is not None
        and crud.user.get_by_email(db, email=user_in.email)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The email is already used"
        )
    if (
        user_in.username is not None
        and crud.user.get_by_username(db, username=user_in.username)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The username is already used"
        )
    return await crud.user.update(db, db_obj=db_user, obj_in=user_in)


@router.delete(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(deps.require_admin)]
)
async def delete_user(
    user_id: UUID4,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Delete the user
    """
    db_user = await crud.user.get(db, id=user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID no exists on the system"
        )

    if db_user.picture:
        has_deleted = await user_picture_manager.delete_user_picture(user_id=user_id)

        if not has_deleted:
            raise HTTPException(status_code=500, detail="Failed to delete user picture")

    await crud.user.remove(db, db_obj=db_user)

    return {"message": "User has been deleted"}


@router.patch(
    path="/new_password",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSimple
)
async def set_new_password_for_current_user(
    data: schemas.ChangePassword,
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Set new password for current user
    """
    if not verify_password(data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have entered the wrong password"
        )

    if verify_password(data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have entered an existing new password"
        )

    await crud.user.update(db, db_obj=current_user, obj_in={"password": data.new_password})

    return {"message": "Successful change password"}


@router.patch(
    path="/{user_id}/new_password",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserSimple,
    dependencies=[Depends(deps.require_admin)]
)
async def set_new_password_by_user_id(
    user_id: UUID4,
    data: schemas.ChangePassword,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Set new password for the user with entered id.
    """
    db_user = await crud.user.get(db, id=user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID no exists on the system"
        )

    if not verify_password(data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have entered the wrong password for an user"
        )

    if verify_password(data.new_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have entered an existing new password for an user"
        )

    await crud.user.update(db, db_obj=db_user, obj_in={"password": data.new_password})

    return {"message": "Successful change password"}


@router.post(
    path="/picture",
    status_code=status.HTTP_201_CREATED,
    # response_model=schemas
)
async def upload_picture_for_current_user(
    file: UploadFile,
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Upload picture for current user.
    """
    try:
        profile_picture_url = await user_picture_manager.save_user_picture(
            user_id=current_user.id,
            filename=file.filename,
            file_contents=await file.read()
        )
        await crud.user.set_picture(db, db_user=current_user, profile_picture_url=profile_picture_url)
    except HTTPException as e:
        raise e

    return {"message": profile_picture_url}


@router.post(
    path="/{user_id}/picture",
    status_code=status.HTTP_201_CREATED,
    # response_model=
    # dependencies=[Depends(deps.require_admin)]
)
async def upload_picture_by_user_id(
    file: UploadFile,
    user_id: UUID4,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Upload picture for the user with entered id.
    """
    db_user = await crud.user.get(db, id=user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID no exists on the system"
        )

    try:
        profile_picture_url = await user_picture_manager.save_user_picture(
            user_id=user_id,
            filename=file.filename,
            file_contents=await file.read()
        )
        await crud.user.set_picture(db, db_user=db_user, profile_picture_url=profile_picture_url)
    except HTTPException as e:
        raise e

    return {"message": profile_picture_url}
    # return {"message": "Zdjęcie użytkownika zostało zapisane"}


@router.patch(
    path="/picture",
    status_code=status.HTTP_200_OK,
    # response_model=schemas
)
async def upload_new_picture_for_current_user(
    file: UploadFile,
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Upload new picture for current user.
    """
    try:
        profile_picture_url = await user_picture_manager.save_user_picture(
            user_id=current_user.id,
            filename=file.filename,
            file_contents=await file.read()
        )
        await crud.user.set_picture(db, db_user=current_user, profile_picture_url=profile_picture_url)
    except HTTPException as e:
        raise e

    return {"message": profile_picture_url}


@router.patch(
    path="/{user_id}/picture",
    status_code=status.HTTP_200_OK,
    # response_model=schemas
    dependencies=[Depends(deps.require_admin)]
)
async def upload_new_picture_by_user_id(
    file: UploadFile,
    user_id: UUID4,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Upload new picture for the user with entered id.
    """
    db_user = await crud.user.get(db, id=user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID no exists on the system"
        )

    try:
        profile_picture_url = await user_picture_manager.save_user_picture(
            user_id=user_id,
            filename=file.filename,
            file_contents=await file.read()
        )
        await crud.user.set_picture(db, db_user=db_user, profile_picture_url=profile_picture_url)
    except HTTPException as e:
        raise e

    return {"message": profile_picture_url}


@router.delete(
    path="/picture",
    status_code=status.HTTP_200_OK,
    # response_model=
)
async def delete_picture_for_current_user(
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Delete picture for current user.
    """
    try:
        has_deleted = await user_picture_manager.delete_user_picture(
            user_id=current_user.id
        )
        await crud.user.delete_picture()

        if not has_deleted:
            raise HTTPException(status_code=500, detail="Failed to delete user picture")

        await crud.user.delete_picture(db, db_user=current_user)

    except HTTPException as e:
        raise e

    return {"message": True}


@router.delete(
    path="/{user_id}/picture",
    status_code=status.HTTP_200_OK,
    # response_model=
    dependencies=[Depends(deps.require_admin)]
)
async def delete_picture_by_user_id(
    user_id: UUID4,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Any:
    """
    Delete picture for the user with entered id.
    """
    db_user = await crud.user.get(db, id=user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this ID no exists on the system"
        )

    try:
        has_deleted = await user_picture_manager.delete_user_picture(
            user_id=user_id
        )

        if not has_deleted:
            raise HTTPException(status_code=500, detail="Failed to delete user picture")

        await crud.user.delete_picture(db, db_user=db_user)
    except HTTPException as e:
        raise e

    return {"message": True}
