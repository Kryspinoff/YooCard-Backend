from app.constants import TilePlatformEnum
from app.constants.tile_type import TileTypeEnum
from app.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Tile(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    type = Column(Enum(TileTypeEnum), nullable=False)
    title = Column(String(32), nullable=False)
    url = Column(String(2048), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    position = Column(Integer, nullable=False)
    icon_url = Column(String(2048), nullable=True)
    short_id = Column(String(length=12), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="tiles")

