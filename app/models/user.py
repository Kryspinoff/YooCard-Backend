from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, Enum, UUID, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.constants import UserRoleEnum
from app.db.base_class import Base


class User(Base):
    """
    Database model for an application user
    """

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    first_name = Column(String(32), nullable=False)
    last_name = Column(String(32), nullable=False)
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    phone_number = Column(String(9), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(UserRoleEnum), unique=False, index=True, nullable=False)
    profile_picture_url = Column(String(2048), nullable=True)
    description = Column(String(256), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tiles = relationship("Tile", back_populates="user")