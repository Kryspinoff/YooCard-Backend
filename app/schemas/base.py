from typing import List, Type, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ResponseWithPagination(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
    total_pages: int
