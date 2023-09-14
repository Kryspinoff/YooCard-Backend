from typing import Union, Optional

from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Tile
from app.schemas import TileCreate, TileUpdate


class CRUDTile(CRUDBase[Tile, TileCreate, TileUpdate]):
    # async def check_tile_exists(self, db: AsyncSession, *, user_id: UUID4, title: str) -> bool:
    #     query = select(self.model).where(
    #         (self.model.user_id == user_id) & (self.model.title.in_(title))
    #     )
    #     result = await db.execute(query)
    #     i

    async def create_tile(self, db: AsyncSession, *, user_id: UUID4, tile: Union[Tile, TileCreate]) -> Optional[Tile]:
        print("Creating tile")
        ...
        return None


tile = CRUDTile(Tile)