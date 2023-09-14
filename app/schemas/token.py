from datetime import timedelta

from pydantic import BaseModel


class Token(BaseModel):
    token: str
    token_type: str
    exp: str


class TokenData(BaseModel):
    exp: timedelta
    sub: str
    role: str = None
