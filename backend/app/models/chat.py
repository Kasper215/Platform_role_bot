"""
Модели: Message, ChatMeta.
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="messages")
    character = relationship("Character", back_populates="messages")


class ChatMeta(Base):
    __tablename__ = "chat_meta"
    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character_chat"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    chat_id = Column(String(100), nullable=False)
    last_message_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    pinned = Column(Boolean, default=False)
    
    # ─── Добавляем колонку для долговременной памяти ИИ ───
    context_summary = Column(Text, nullable=True) # <-- ДОБАВИЛИ ТУТ