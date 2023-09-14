from app import crud, schemas
from app.constants import UserRoleEnum
from app.core.config import settings
from sqlalchemy.orm import Session


async def init_db(db: Session) -> None:
    # Create Super Admin
    super_admin = await crud.user.get_by_username(db, username=settings.FIRST_SUPER_ADMIN_USERNAME)
    if not super_admin:
        super_admin_in = schemas.UserCreateInDB(
            first_name=settings.FIRST_SUPER_ADMIN_FIRST_NAME,
            last_name=settings.FIRST_SUPER_ADMIN_LAST_NAME,
            username=settings.FIRST_SUPER_ADMIN_USERNAME,
            email=settings.FIRST_SUPER_ADMIN_EMAIL,
            password=settings.FIRST_SUPER_ADMIN_PASSWORD,
            role=UserRoleEnum.ADMIN
        )
        await crud.user.create(db, obj_in=super_admin_in)
