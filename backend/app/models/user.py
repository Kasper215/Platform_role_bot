"""
Модель пользователя.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    characters = relationship(
        "Character", back_populates="owner", cascade="all, delete-orphan"
    )
    messages = relationship("Message", back_populates="user")
    likes = relationship(
        "CharacterLike", back_populates="user", cascade="all, delete-orphan"
    )
