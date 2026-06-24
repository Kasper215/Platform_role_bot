"""
API-роутер: персонажи.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from typing import List, Optional
from collections import Counter
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.character import Character, CharacterLike
from app.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListItem,
    TagInfo,
)
from app.services.avatar import get_or_create_avatar

router = APIRouter(prefix="/characters", tags=["characters"])


# ─── Хелперы ────────────────────────────────────────────────────────────────

def _split_tags(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [t.strip().lower() for t in raw.split(",") if t.strip()]


def _join_tags(tags: Optional[List[str]]) -> Optional[str]:
    if not tags:
        return None
    return ",".join(sorted({t.strip().lower() for t in tags if t.strip()}))


def _to_list_item(char: Character, user_id: int) -> CharacterListItem:
    liked = any(l.user_id == user_id for l in (char.likes or []))
    return CharacterListItem(
        id=char.id,
        name=char.name,
        description=char.description,
        avatar_url=char.avatar_url,
        tags=_split_tags(char.tags),
        is_public=char.is_public,
        is_nsfw=char.is_nsfw,
        is_featured=bool(char.is_featured),
        chat_count=int(char.chat_count or 0),
        like_count=int(char.like_count or 0),
        views=int(char.views or 0),
        is_liked=liked,
        owner_id=char.owner_id,
        created_at=char.created_at,
    )


def _to_full_response(char: Character, user_id: int) -> CharacterResponse:
    liked = any(l.user_id == user_id for l in (char.likes or []))
    return CharacterResponse(
        id=char.id,
        owner_id=char.owner_id,
        name=char.name,
        persona=char.persona,
        description=char.description,
        greeting=char.greeting,
        avatar_url=char.avatar_url,
        tags=_split_tags(char.tags),
        is_public=char.is_public,
        model_id=char.model_id,
        is_nsfw=char.is_nsfw,
        is_featured=bool(char.is_featured),
        chat_count=int(char.chat_count or 0),
        like_count=int(char.like_count or 0),
        views=int(char.views or 0),
        is_liked=liked,
        created_at=char.created_at,
        updated_at=char.updated_at,
    )


# ─── Эндпоинты ──────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CharacterListItem])
def list_characters(
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    sort: str = Query("new", pattern="^(new|popular|trending)$"),
    limit: int = Query(48, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Список персонажей (свои + публичные) с поиском/тегами/сортировкой."""
    q = db.query(Character).filter(
        (Character.owner_id == current_user.id) | (Character.is_public == True)
    )

    if search:
        like = f"%{search.lower()}%"
        q = q.filter(
            or_(
                func.lower(Character.name).like(like),
                func.lower(func.coalesce(Character.description, "")).like(like),
                func.lower(func.coalesce(Character.tags, "")).like(like),
            )
        )

    if tag:
        q = q.filter(
            func.lower(func.coalesce(Character.tags, "")).like(f"%{tag.lower()}%")
        )

    if sort == "popular":
        q = q.order_by(desc(Character.like_count), desc(Character.views))
    elif sort == "trending":
        q = q.order_by(
            desc(Character.is_featured),
            desc(Character.chat_count),
            desc(Character.views),
        )
    else:
        q = q.order_by(desc(Character.created_at))

    chars = q.offset(offset).limit(limit).all()
    return [_to_list_item(c, current_user.id) for c in chars]


@router.get("/featured", response_model=List[CharacterListItem])
def get_featured(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Рекомендованные персонажи для главной."""
    chars = (
        db.query(Character)
        .filter(Character.is_public == True)
        .order_by(
            desc(Character.is_featured),
            desc(Character.like_count),
            desc(Character.views),
            desc(Character.chat_count),
        )
        .limit(12)
        .all()
    )
    return [_to_list_item(c, current_user.id) for c in chars]


@router.get("/tags", response_model=List[TagInfo])
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Список тегов с количеством."""
    chars = (
        db.query(Character)
        .filter(
            (Character.owner_id == current_user.id) | (Character.is_public == True),
            Character.tags != None,
        )
        .all()
    )
    counter: Counter[str] = Counter()
    for c in chars:
        for t in _split_tags(c.tags):
            counter[t] += 1
    return [
        TagInfo(name=name, count=count) for name, count in counter.most_common(40)
    ]


@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Полный профиль персонажа (+1 просмотр)."""
    char = (
        db.query(Character)
        .filter(
            Character.id == character_id,
            (Character.owner_id == current_user.id) | (Character.is_public == True),
        )
        .first()
    )
    if not char:
        raise HTTPException(404, "Персонаж не найден")

    char.views = int(char.views or 0) + 1
    db.commit()
    db.refresh(char)
    return _to_full_response(char, current_user.id)


@router.post("/", response_model=CharacterResponse)
def create_character(
    character: CharacterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Создать нового персонажа."""
    avatar_url = get_or_create_avatar(character.name, character.avatar_url)

    new_char = Character(
        owner_id=current_user.id,
        name=character.name,
        persona=character.persona,
        description=character.description,
        greeting=character.greeting,
        avatar_url=avatar_url,
        tags=_join_tags(character.tags),
        is_public=character.is_public,
        model_id=character.model_id,
        is_nsfw=character.is_nsfw,
    )
    db.add(new_char)
    db.commit()
    db.refresh(new_char)
    return _to_full_response(new_char, current_user.id)


@router.put("/{character_id}", response_model=CharacterResponse)
def update_character(
    character_id: int,
    data: CharacterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Редактировать персонажа (только владелец)."""
    char = (
        db.query(Character)
        .filter(Character.id == character_id, Character.owner_id == current_user.id)
        .first()
    )
    if not char:
        raise HTTPException(404, "Персонаж не найден")

    update_data = data.model_dump(exclude_unset=True)
    if "tags" in update_data:
        char.tags = _join_tags(update_data.pop("tags"))
    for key, value in update_data.items():
        setattr(char, key, value)

    db.commit()
    db.refresh(char)
    return _to_full_response(char, current_user.id)


@router.delete("/{character_id}")
def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Удалить персонажа (только владелец)."""
    char = (
        db.query(Character)
        .filter(Character.id == character_id, Character.owner_id == current_user.id)
        .first()
    )
    if not char:
        raise HTTPException(404, "Персонаж не найден")
    db.delete(char)
    db.commit()
    return {"message": "Персонаж удалён"}


@router.post("/{character_id}/like")
def like_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Лайкнуть персонажа."""
    char = (
        db.query(Character)
        .filter(
            Character.id == character_id,
            (Character.owner_id == current_user.id) | (Character.is_public == True),
        )
        .first()
    )
    if not char:
        raise HTTPException(404, "Персонаж не найден")

    existing = (
        db.query(CharacterLike)
        .filter(
            CharacterLike.user_id == current_user.id,
            CharacterLike.character_id == character_id,
        )
        .first()
    )
    if existing:
        return {"liked": True, "like_count": int(char.like_count or 0)}

    like = CharacterLike(user_id=current_user.id, character_id=character_id)
    db.add(like)
    char.like_count = int(char.like_count or 0) + 1
    db.commit()
    db.refresh(char)
    return {"liked": True, "like_count": int(char.like_count or 0)}


@router.delete("/{character_id}/like")
def unlike_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Убрать лайк с персонажа."""
    existing = (
        db.query(CharacterLike)
        .filter(
            CharacterLike.user_id == current_user.id,
            CharacterLike.character_id == character_id,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        char = db.query(Character).filter(Character.id == character_id).first()
        if char:
            char.like_count = max(0, int(char.like_count or 0) - 1)
        db.commit()

    char = db.query(Character).filter(Character.id == character_id).first()
    return {
        "liked": False,
        "like_count": int(char.like_count or 0) if char else 0,
    }
