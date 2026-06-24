"""
Модели: Character, CharacterLike.
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Boolean, 
    UniqueConstraint, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    # === Базовые ===
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    persona = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    greeting = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    tags = Column(String(500), nullable=True)
    
    # === Статус ===
    is_public = Column(Boolean, default=False)
    model_id = Column(String(100), default="auto")
    is_nsfw = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    # === Статистика ===
    chat_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # === НОВЫЕ ПОЛЯ ДЛЯ ПОЛНОЦЕННЫХ ПЕРСОНАЖЕЙ ===
    
    # Личность
    personality = Column(Text, nullable=True)         # характер: "дерзкий, харизматичный, скрытный"
    backstory = Column(Text, nullable=True)          # предыстория: "Был изгнан из своего клана..."
    motivation = Column(Text, nullable=True)         # мотивация: "Хочет найти свой потерянный дом"
    speech_style = Column(Text, nullable=True)       # стиль речи: "Говорит короткими рублеными фразами"
    catchphrase = Column(String(200), nullable=True) # коронная фраза: "Я знаю больше, чем говорю."
    
    # Сцена (контекст для ролевой игры)
    scene_title = Column(String(255), nullable=True)
    scene_description = Column(Text, nullable=True)
    scene_setting = Column(String(255), nullable=True)
    
    # Анкетные данные
    age = Column(Integer, nullable=True)
    gender = Column(String(50), nullable=True)
    race = Column(String(100), nullable=True)
    occupation = Column(String(255), nullable=True)
    
    # Дополнительные данные (JSON)
    traits = Column(JSON, nullable=True)             # ["харизматичный", "скрытный", "опасный"]
    likes = Column(JSON, nullable=True)              # ["звёзды", "тишина", "холодный чай"]
    fears = Column(JSON, nullable=True)              # ["предательство", "одиночество"]
    
    # === Даты ===
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # === Связи ===
    owner = relationship("User", back_populates="characters")
    messages = relationship("Message", back_populates="character")
    likes = relationship(
        "CharacterLike", back_populates="character", cascade="all, delete-orphan"
    )


class CharacterLike(Base):
    __tablename__ = "character_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character_like"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="likes")
    character = relationship("Character", back_populates="likes")