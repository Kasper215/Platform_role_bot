from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    display_name = Column(String(100), nullable=True)  # красивое имя для профиля
    bio = Column(Text, nullable=True)                  # описание профиля
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    characters = relationship("Character", back_populates="owner", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user")
    likes = relationship("CharacterLike", back_populates="user", cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    persona = Column(Text, nullable=False)
    description = Column(Text, nullable=True)   # краткое описание для карточек
    greeting = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    tags = Column(String(500), nullable=True)   # теги через запятую
    is_public = Column(Boolean, default=False)
    model_id = Column(String(100), default="auto")
    is_nsfw = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)  # рекомендованные/трендовые
    chat_count = Column(Integer, default=0)       # сколько чатов заведено
    like_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="characters")
    messages = relationship("Message", back_populates="character")
    likes = relationship("CharacterLike", back_populates="character", cascade="all, delete-orphan")


class CharacterLike(Base):
    """Один лайк на пользователя/персонажа."""
    __tablename__ = "character_likes"
    __table_args__ = (UniqueConstraint("user_id", "character_id", name="uq_user_character_like"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="likes")
    character = relationship("Character", back_populates="likes")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="messages")
    character = relationship("Character", back_populates="messages")


class ChatMeta(Base):
    """Индекс для быстрого списка чатов пользователя + закрепление."""
    __tablename__ = "chat_meta"
    __table_args__ = (UniqueConstraint("user_id", "character_id", name="uq_user_character_chat"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    chat_id = Column(String(100), nullable=False)
    last_message_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    pinned = Column(Boolean, default=False)
