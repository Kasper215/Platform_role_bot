from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List


# ─── User schemas ──────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    username: Optional[str] = None


# ─── Character schemas ─────────────────────────────────────────────────────────
class CharacterCreate(BaseModel):
    name: str
    persona: str
    description: Optional[str] = None
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False
    model_id: str = "auto"
    is_nsfw: bool = False


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    persona: Optional[str] = None
    description: Optional[str] = None
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    model_id: Optional[str] = None
    is_nsfw: Optional[bool] = None


class CharacterResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    persona: str
    description: Optional[str] = None
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: List[str] = []
    is_public: bool
    model_id: str
    is_nsfw: bool
    is_featured: bool = False
    chat_count: int = 0
    like_count: int = 0
    views: int = 0
    is_liked: bool = False  # лайкнул ли текущий юзер
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CharacterListItem(BaseModel):
    """Лёгкая карточка для галереи/списков — без persona/greeting."""
    id: int
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: List[str] = []
    is_public: bool
    is_nsfw: bool
    is_featured: bool = False
    chat_count: int = 0
    like_count: int = 0
    views: int = 0
    is_liked: bool = False
    owner_id: int
    created_at: datetime


class TagInfo(BaseModel):
    name: str
    count: int


# ─── Message schemas ───────────────────────────────────────────────────────────
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


# ─── Chat schemas ──────────────────────────────────────────────────────────────
class ChatResponse(BaseModel):
    id: int
    character_id: int
    messages: List[MessageResponse]

    model_config = ConfigDict(from_attributes=True)


class ChatListItem(BaseModel):
    """Строка боковой панели чатов."""
    character_id: int
    chat_id: str
    character_name: str
    avatar_url: Optional[str] = None
    is_nsfw: bool = False
    last_content: Optional[str] = None
    last_role: Optional[str] = None
    last_message_at: Optional[datetime] = None
    pinned: bool = False


# ─── Token schemas ─────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
