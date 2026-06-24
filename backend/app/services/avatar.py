"""
Генерация аватаров для персонажей.
Используем DiceBear API для создания уникальных аватарок на основе имени.
"""
import hashlib
from typing import Optional
from app.core.config import AVATARS_DIR


def generate_avatar_url(name: str) -> str:
    """
    Генерирует URL аватара через DiceBear (стиль — adventurer).
    Аватары уникальны для каждого имени (детерминированный хеш).
    """
    seed = hashlib.md5(name.encode()).hexdigest()[:8]
    return f"https://api.dicebear.com/9.x/adventurer-neutral/svg?seed={seed}&backgroundColor=b6e3f4,c0aede,d1d4f9"


def get_or_create_avatar(name: str, existing_url: Optional[str] = None) -> str:
    """
    Возвращает URL аватара.
    Если у персонажа ещё нет аватара — генерируем новый.
    """
    if existing_url:
        return existing_url
    return generate_avatar_url(name)
