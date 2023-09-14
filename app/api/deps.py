import logging
from typing import Generator, Optional

from app import crud, models, schemas
from app.constants import UserRoleEnum
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from pydantic import ValidationError
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login", auto_error=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session


async def get_current_user(
    # token: str = Depends(oauth2_scheme),
    access_token: str = Cookie(None),
    db: AsyncSession = Depends(get_async_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token=access_token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("sub") is None:
            raise credentials_exception
        token_data = schemas.TokenData(**payload)
    except (AttributeError, jwt.JWTError, ValidationError):
        logger.error("Error Decoding Token", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )

    user = await crud.user.get_by_username(db, username=token_data.sub)

    if not user:
        raise credentials_exception
    if not token_data.role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user


async def get_current_user_or_none(
    access_token: str = Depends(optional_oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> Optional[models.User]:
    if not access_token:
        return None

    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token_data = schemas.TokenData(**payload)
    except (jwt.JWTError, ValidationError):
        logger.error("Error Decoding Token", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )

    user = await crud.user.get_by_username(db, username=token_data.sub)
    print("Authenticated")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return user


def require_admin(
    user: models.User = Depends(get_current_user)
) -> Optional[models.User]:
    if user.role not in [UserRoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin privileges required"
        )
    return user


def disabled_endpoint():
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Endpoint temporarily disabled"
    )
