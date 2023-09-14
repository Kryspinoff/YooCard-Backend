# from datetime import datetime
# from typing import Optional
#
# from pydantic import BaseModel, Field, EmailStr, UUID4, conint
# from sqlalchemy import Integer
#
#
# class IconBase(BaseModel):
#     name: str = Field(..., max_length=32)
#
#
# class IconCreate(IconBase):
#     pass
#
#
# class IconUpdate(IconBase):
#     pass
#
#
# class IconCreateInDB(IconCreate):
#     url: str = Field(..., max_length=2048)
#
#
# class IconInDBBase(IconCreateInDB):
#     id: int
#
#     class Config:
#         from_attributes = True
#
#
# class Icon(IconInDBBase):
#     pass
#
#
# class IconInDB(IconInDBBase):
#     pass
