from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.future import select

from app.db.base import Base
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, BaseModel
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import inspect, func
from sqlalchemy.ext.asyncio import AsyncSession

# Define custom types for SQLAlchemy model, and Pydantic schemas
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
T = TypeVar("T", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """Base class that can be extend by other action classes.
           Provides basic CRUD and listing operations.
        :param model: The SQLAlchemy model
        :type model: Type[ModelType]
        """
        self.model = model

    # @property
    # def relations(self):
    #     mapper = inspect(self.model)
    #     relationships = mapper.relationships
    #     print(relationships)
    #     for relationship in relationships:
    #         print(getattr(self.model, relationship.key))
    #     return relationships

    async def get_multi(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> tuple[List[ModelType], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(query.alias())
        total_count: int = await db.scalar(count_query)
        result = await db.execute(query)
        db_models = [db_model for db_model in result.unique().scalars().all()]
        return db_models, total_count

    async def get(self, db: AsyncSession, id: Union[UUID4, int], including: list[T]) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)

        if including:
            for rel in including:
                stmt = stmt.options(selectinload(getattr(self.model, rel.__tablename__)))

        result = await db.execute(stmt)
        return result.scalar()
        #
        # stmt = select(self.model).where(self.model.id == id)
        # result = await db.execute(stmt)
        # return result.scalar()

    async def create(self, db: AsyncSession, *, obj_in: Union[CreateSchemaType, ModelType]) -> ModelType:
        db_obj = obj_in
        if not isinstance(obj_in, self.model):
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def create_multi(
        self, db: AsyncSession, *, objs_in: List[Union[CreateSchemaType, ModelType]]
    ) -> List[ModelType]:
        db_objs = []

        for obj_in in objs_in:
            if not isinstance(obj_in, self.model):
                obj_in_data = jsonable_encoder(obj_in)
                db_obj = self.model(**obj_in_data)
                db_objs.append(db_obj)
            else:
                db_objs.append(obj_in)

        db.add_all(db_objs)
        await db.commit()
        return db_objs

    @staticmethod
    async def update(
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: [UpdateSchemaType, Dict[str, Any]]
    ):
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    def remove(db: Session, *, db_obj: ModelType) -> ModelType:
        db.delete(db_obj)
        db.commit()
        return db_obj

    def _apply_filters(self, query, **filters):
        for field, value in filters.items():
            if value is None:
                continue

            # Handle fields that are in related models
            if '__' in field:
                related_model_name, related_field_name = field.split('__')
                related_model = getattr(self.model, related_model_name).property.mapper.class_

                # Handle many-to-many relationships
                if related_model_name in self.model.__mapper__.relationships.keys():
                    related_table = self.model.__mapper__.relationships[related_model_name].secondary
                    related_column = getattr(related_model, related_field_name, None)
                    if related_column is None:
                        continue
                    if isinstance(value, str):
                        query = query.join(related_table).join(related_model).where(related_column.ilike(f"%{value}%"))
                    else:
                        query = query.join(related_table).join(related_model).where(related_column == value)

                # Handle one-to-many relationships
                elif related_model_name in self.model.__mapper__.relationships.values():
                    related_column = getattr(related_model, related_field_name, None)
                    if related_column is None:
                        continue
                    if isinstance(value, str):
                        query = query.join(getattr(self.model, related_model_name)).where(related_column.ilike(f"%{value}%"))
                    else:
                        query = query.join(getattr(self.model, related_model_name)).where(related_column == value)

            # Handle fields that are in the main model
            else:
                column = getattr(self.model, field, None)
                if column is None:
                    continue
                if isinstance(value, str):
                    query = query.where(column.ilike(f"%{value}%"))
                else:
                    query = query.where(column == value)
        return query

    def _query_with_all_joined_relationships(self, query=None) -> ModelType:
        mapper = inspect(self.model)

        if query is None:
            query = select(self.model)

        for relationship in mapper.relationships:
            # `backref` relationships have `uselist=True`
            # and should not be included in the query
            if relationship.backref:
                continue
            query = query.options(joinedload(relationship.key))

        return query

    def _query_with_joined_relationships(self, relationships: list[ModelType], query=None):
        if query is None:
            query = select(self.model)

        for relationship in relationships:
            query = query.options(joinedload(relationship))

        return query
