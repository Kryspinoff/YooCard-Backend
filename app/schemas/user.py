import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, UUID4, field_validator
# import typing
#
# if typing.TYPE_CHECKING:
#     from app.schemas.user_tile import UserTile

from app.schemas.tile import Tile


class UserBase(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=32,
        example="jankowalski",
    )
    first_name: str = Field(
        None,
        alias="firstName",
        min_length=2,
        max_length=32,
        example="Jan"
    )
    last_name: str = Field(
        None,
        alias="lastName",
        min_length=2,
        max_length=32,
        example="Kowalski"
    )
    email: EmailStr = Field(
        example="jankowalski@example.com"
    )
    phone_number: Optional[str] = Field(
        None,
        alias="phoneNumber",
        min_length=9,
        max_length=9,
        example="500500500"
    )

    class Config:
        populate_by_name = True
        alias_generator = lambda s: re.sub(r'_([a-z])', lambda match: match.group(1).upper(), s)


class UserCreate(UserBase):
    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        example="jankowalski",
    )
    first_name: str = Field(
        ...,
        alias="firstName",
        min_length=2,
        max_length=32,
        example="Jan"
    )
    last_name: str = Field(
        ...,
        alias="lastName",
        min_length=2,
        max_length=32,
        example="Kowalski"
    )
    email: EmailStr = Field(
        ...,
        example="jankowalski@example.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        example="Password@132",
    )
    phone_number: Optional[str] = Field(
        None,
        alias="phoneNumber",
        min_length=9,
        max_length=16,
        example="500500500"
    )

    @field_validator("password")
    def validate_password(cls, value):
        if (
            any(c.isupper() for c in value) and
            any(c.islower() for c in value) and
            any(c.isdigit() for c in value) and
            any(c in '''?!@#$%^&*()_-{}[],.<>;:''' for c in value) and
            len(value) >= 8
        ):
            return value
        raise ValueError(
            "Password must contain at least one lowercase letter, one uppercase letter, "
            "one number, one of the special characters: #?!@$%^&*- and be at least 8 characters long."
        )

    # class Config:
    #     allow_population_by_field_name = True
    #     alias_generator = lambda s: s.replace("_", "")


class UserUpdate(UserBase):
    pass


class UserCreateInDB(UserCreate):
    role: str
    is_active: Optional[bool] = None


class UserSimpleInDBBase(UserBase):
    id: UUID4
    role: str
    created_at: datetime
    updated_at: datetime
    profile_picture_url: Optional[str]

    class Config:
        from_attributes = True


class UserSimple(UserSimpleInDBBase):
    pass


class UserInDBBase(UserSimpleInDBBase):
    tiles: list[Tile]

    class Config:
        arbitrary_types_allowed = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    is_active: bool
    hashed_password: str


class ChangePassword(BaseModel):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        example="Password@132",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        example="Password@1321",
    )

    @field_validator("password")
    def validate_password(cls, value):
        if (
            any(c.isupper() for c in value) and
            any(c.islower() for c in value) and
            any(c.isdigit() for c in value) and
            any(c in '''?!@#$%^&*()_-{}[],.<>;:''' for c in value) and
            len(value) >= 8
        ):
            return value
        raise ValueError(
            "Password must contain at least one lowercase letter, one uppercase letter, "
            "one number, one of the special characters: #?!@$%^&*- and be at least 8 characters long."
        )

# from app.models import ContactLink
# UserInDBBase.update_forward_refs()
# User.update_forward_refs()
# UserInDB.update_forward_refs()