from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4

from app.schemas import Tile


class ResponseProfile(BaseModel):
    id: UUID4
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str]
    tiles: list[Tile]
    profile_picture_url: Optional[str]

    class Config:
        arbitrary_types_allowed = True
