from typing import Any, Dict, Optional, Union, List

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import schemas
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase, ModelType, T
from app.models import Tile
from app.models.user import User
from app.schemas.user import UserCreateInDB, UserUpdate
from sqlalchemy.orm import Session, selectinload


class CRUDUser(CRUDBase[User, UserCreateInDB, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.email == email)
        result = await db.execute(stmt)
        user = result.scalar()
        return user
        # return db.query(self.model).filter(self.model.email == email).first()

    async def get_by_username(self, db: AsyncSession, *, username: str, including: list[T] = None) -> Optional[User]:
        stmt = select(self.model).where(self.model.username == username)

        if including:
            for rel in including:
                print(rel.__tablename__)
                stmt = stmt.options(selectinload(getattr(self.model, rel.__tablename__)))
                #
                # if rel.__tablename__ == "tiles":
                #     stmt = stmt.options(selectinload(self.model.tiles).selectinload(Tile.icon))

        result = await db.execute(stmt)
        return result.scalar()
        # return db.query(self.model).filter(self.model.username == username).first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreateInDB) -> User:
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone_number=obj_in.phone_number,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role
        )
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: [UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, password: str, email: str = None, username: str = None) -> Optional[User]:
        if email:
            user = await self.get_by_email(db, email=email)
        elif username:
            user = await self.get_by_username(db, username=username)
        else:
            return None

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def set_picture(db: AsyncSession, *, db_user: User, profile_picture_url: str) -> User:
        db_user.profile_picture_url = profile_picture_url
        await db.commit()
        return db_user

    @staticmethod
    async def delete_picture(db: AsyncSession, *, db_user: User) -> User:
        db_user.profile_picture_url = None
        await db.commit()
        return db_user

    # async def add_contact_links(self, db: AsyncSession, *, user: User, contact_links: ContactLink):

    # async def get_multi(
    #     self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    # ) -> tuple[List[ModelType], int]:
    #     query = select(self.model)
    #     count_query = select(func.count()).select_from(query.alias())
    #     total_count: int = await db.scalar(count_query)
    #     query = query.options(selectinload(self.model.contact_links))
    #     result = await db.execute(query)
    #     db_models = [db_model for db_model in result.unique().scalars().all()]
    #     return db_models, total_count


user = CRUDUser(User)