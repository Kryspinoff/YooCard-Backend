from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, UUID4, conint
from sqlalchemy import Integer

from app.constants import TileTypeEnum


class TileBase(BaseModel):
    type: TileTypeEnum = Field(
        ...
    )
    title: str = Field(
        ...,
        max_length=32,
    )
    url: str = Field(
        ...,
        max_length=2048,
    )
    active: Optional[bool] = True
    position: conint = Field(
        ...,
        ge=0,
        lt=100
    )


class TileCreate(TileBase):
    pass


class TileUpdate(TileBase):
    pass


class TileCreateInDB(TileBase):
    pass


class TileInDBBase(TileBase):
    id: UUID4
    user_id: UUID4
    short_id: Optional[str]

    class Config:
        from_attributes = True


class Tile(TileInDBBase):
    pass


class TileInDB(TileInDBBase):
    pass
