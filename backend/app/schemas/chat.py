"""
Pydantic-схемы для сообщений и чатов.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class MessageCreate(BaseModel):
    character_id: int
    content: str


class MessageResponse(BaseModel):
    id: int
    chat_id: str
    user_id: int
    character_id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    id: int
    character_id: int
    messages: List[MessageResponse]

    model_config = ConfigDict(from_attributes=True)


class ChatListItem(BaseModel):
    character_id: int
    chat_id: str
    character_name: str
    avatar_url: Optional[str] = None
    is_nsfw: bool = False
    last_content: Optional[str] = None
    last_role: Optional[str] = None
    last_message_at: Optional[datetime] = None
    pinned: bool = False
