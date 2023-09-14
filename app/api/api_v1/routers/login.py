from datetime import timedelta, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.core import security
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordRequestFormStrict

from app.core.config import settings

router = APIRouter(
    prefix="/login",
    tags=["login"]
)


@router.post(
    path="",
    # response_model=schemas.Token,
    status_code=status.HTTP_200_OK
)
async def login_user(
    response: Response,
    db: AsyncSession = Depends(deps.get_async_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    if "@" in form_data.username:
        user = await crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    else:
        user = await crud.user.authenticate(db, username=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username/email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = security.create_access_token(
        user=user,
        expires_delta=access_token_expires
    )

    response.set_cookie(key="access_token", value=token, httponly=True, secure=True, expires=int(access_token_expires.total_seconds()))
    response.set_cookie(key="is_logged_in", value="true", expires=int(access_token_expires.total_seconds()))

    return {"detail": "Successfully logged"}
    # return response
    # return schemas.Token(
    #     token=security.create_access_token(
    #         user=user,
    #         expires_delta=access_token_expires
    #     ),
    #     token_type="Bearer",
    #     exp=str(access_token_expires.seconds)
    # )
