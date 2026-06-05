from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, List

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Character schemas
class CharacterCreate(BaseModel):
    name: str
    persona: str
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: bool = False
    model_id: str = "auto"
    is_nsfw: bool = False

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    persona: Optional[str] = None
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: Optional[bool] = None
    model_id: Optional[str] = None

class CharacterResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    persona: str
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: bool
    model_id: str
    is_nsfw: bool  # 🆕 добавить
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Message schemas
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

class ChatHistoryResponse(BaseModel):
    messages: List[MessageResponse]
    character: CharacterResponse

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None