"""
Pydantic-схемы для персонажей.
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


# ============================================================
# БАЗОВЫЕ СХЕМЫ
# ============================================================

class CharacterBase(BaseModel):
    """Базовые поля персонажа."""
    name: str
    persona: str
    description: Optional[str] = None
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False
    model_id: str = "auto"
    is_nsfw: bool = False
    
    # === НОВЫЕ ПОЛЯ ДЛЯ ПОЛНОЦЕННЫХ ПЕРСОНАЖЕЙ ===
    
    # Личность и характер
    personality: Optional[str] = None          # характер, черты
    backstory: Optional[str] = None            # предыстория
    motivation: Optional[str] = None           # мотивация
    speech_style: Optional[str] = None         # стиль речи
    catchphrase: Optional[str] = None          # коронная фраза
    
    # Сцена (контекст для ролевой игры)
    scene_title: Optional[str] = None
    scene_description: Optional[str] = None
    scene_setting: Optional[str] = None        # место действия
    
    # Анкетные данные
    age: Optional[int] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    occupation: Optional[str] = None
    
    # Дополнительные данные (JSON-поля)
    traits: Optional[List[str]] = None         # черты характера
    likes: Optional[List[str]] = None          # что любит
    fears: Optional[List[str]] = None          # чего боится


# ============================================================
# СОЗДАНИЕ / ОБНОВЛЕНИЕ
# ============================================================

class CharacterCreate(CharacterBase):
    """Создание персонажа."""
    pass


class CharacterUpdate(BaseModel):
    """Обновление персонажа (все поля опциональны)."""
    name: Optional[str] = None
    persona: Optional[str] = None
    description: Optional[str] = None
    greeting: Optional[str] = None
    avatar_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    model_id: Optional[str] = None
    is_nsfw: Optional[bool] = None
    
    # Новые поля
    personality: Optional[str] = None
    backstory: Optional[str] = None
    motivation: Optional[str] = None
    speech_style: Optional[str] = None
    catchphrase: Optional[str] = None
    scene_title: Optional[str] = None
    scene_description: Optional[str] = None
    scene_setting: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    occupation: Optional[str] = None
    traits: Optional[List[str]] = None
    likes: Optional[List[str]] = None
    fears: Optional[List[str]] = None


# ============================================================
# ОТВЕТЫ (RESPONSE)
# ============================================================

class CharacterResponse(BaseModel):
    """Полный ответ с персонажем."""
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
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime
    
    # Новые поля
    personality: Optional[str] = None
    backstory: Optional[str] = None
    motivation: Optional[str] = None
    speech_style: Optional[str] = None
    catchphrase: Optional[str] = None
    scene_title: Optional[str] = None
    scene_description: Optional[str] = None
    scene_setting: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    race: Optional[str] = None
    occupation: Optional[str] = None
    traits: List[str] = []
    likes: List[str] = []
    fears: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class CharacterListItem(BaseModel):
    """Краткий ответ для списка персонажей."""
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
    
    # Новые поля (краткая версия)
    personality: Optional[str] = None
    catchphrase: Optional[str] = None
    scene_title: Optional[str] = None
    traits: List[str] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ============================================================

class TagInfo(BaseModel):
    """Информация о теге."""
    name: str
    count: int


class CharacterStats(BaseModel):
    """Статистика по персонажам."""
    total: int
    public: int
    featured: int
    nsfw: int