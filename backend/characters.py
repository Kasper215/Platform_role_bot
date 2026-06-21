from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from typing import List, Optional
from collections import Counter
import database
import models
import schemas
import auth

router = APIRouter(prefix="/characters", tags=["characters"])


# ─── Хелперы для тегов (хранятся строкой через запятую) ────────────────────────
def _split_tags(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [t.strip().lower() for t in raw.split(",") if t.strip()]


def _join_tags(tags: Optional[List[str]]) -> Optional[str]:
    if not tags:
        return None
    return ",".join(sorted({t.strip().lower() for t in tags if t.strip()}))


def _to_list_item(char: models.Character, user_id: int) -> schemas.CharacterListItem:
    liked = any(l.user_id == user_id for l in (char.likes or []))
    return schemas.CharacterListItem(
        id=char.id,
        name=char.name,
        description=getattr(char, "description", None),
        avatar_url=char.avatar_url,
        tags=_split_tags(getattr(char, "tags", None)),
        is_public=char.is_public,
        is_nsfw=char.is_nsfw,
        is_featured=bool(getattr(char, "is_featured", False)),
        chat_count=int(getattr(char, "chat_count", 0) or 0),
        like_count=int(getattr(char, "like_count", 0) or 0),
        views=int(getattr(char, "views", 0) or 0),
        is_liked=liked,
        owner_id=char.owner_id,
        created_at=char.created_at,
    )


def _to_full_response(char: models.Character, user_id: int) -> schemas.CharacterResponse:
    liked = any(l.user_id == user_id for l in (char.likes or []))
    return schemas.CharacterResponse(
        id=char.id,
        owner_id=char.owner_id,
        name=char.name,
        persona=char.persona,
        description=getattr(char, "description", None),
        greeting=char.greeting,
        avatar_url=char.avatar_url,
        tags=_split_tags(getattr(char, "tags", None)),
        is_public=char.is_public,
        model_id=char.model_id,
        is_nsfw=char.is_nsfw,
        is_featured=bool(getattr(char, "is_featured", False)),
        chat_count=int(getattr(char, "chat_count", 0) or 0),
        like_count=int(getattr(char, "like_count", 0) or 0),
        views=int(getattr(char, "views", 0) or 0),
        is_liked=liked,
        created_at=char.created_at,
        updated_at=char.updated_at,
    )


# ─── Список персонажей (видит свои + публичные) с поиском/тегами/сортировкой ──
@router.get("/", response_model=List[schemas.CharacterListItem])
def list_characters(
    search: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    sort: str = Query("new", pattern="^(new|popular|trending|trending)$"),
    limit: int = Query(48, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    q = db.query(models.Character).filter(
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True)
    )

    if search:
        like = f"%{search.lower()}%"
        q = q.filter(
            or_(
                func.lower(models.Character.name).like(like),
                func.lower(func.coalesce(models.Character.description, "")).like(like),
                func.lower(func.coalesce(models.Character.tags, "")).like(like),
            )
        )

    if tag:
        q = q.filter(
            func.lower(func.coalesce(models.Character.tags, "")).like(f"%{tag.lower()}%")
        )

    if sort == "popular":
        q = q.order_by(desc(models.Character.like_count), desc(models.Character.views))
    elif sort == "trending":
        q = q.order_by(
            desc(models.Character.is_featured),
            desc(models.Character.chat_count),
            desc(models.Character.views),
        )
    else:  # new
        q = q.order_by(desc(models.Character.created_at))

    chars = q.offset(offset).limit(limit).all()
    return [_to_list_item(c, current_user.id) for c in chars]


# ─── Рекомендованные/трендовые для главной ────────────────────────────────────
@router.get("/featured", response_model=List[schemas.CharacterListItem])
def get_featured(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    chars = (
        db.query(models.Character)
        .filter(models.Character.is_public == True)
        .order_by(
            desc(models.Character.is_featured),
            desc(models.Character.like_count),
            desc(models.Character.views),
            desc(models.Character.chat_count),
        )
        .limit(12)
        .all()
    )
    return [_to_list_item(c, current_user.id) for c in chars]


# ─── Доступные теги со счётчиком ───────────────────────────────────────────────
@router.get("/tags", response_model=List[schemas.TagInfo])
def get_tags(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    chars = db.query(models.Character).filter(
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True),
        models.Character.tags != None,
    ).all()
    counter: Counter[str] = Counter()
    for c in chars:
        for t in _split_tags(c.tags):
            counter[t] += 1
    return [schemas.TagInfo(name=name, count=count) for name, count in counter.most_common(40)]


# ─── Полный профиль персонажа (с инкрементом просмотров) ──────────────────────
@router.get("/{character_id}", response_model=schemas.CharacterResponse)
def get_character(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    char = db.query(models.Character).filter(
        models.Character.id == character_id,
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True),
    ).first()
    if not char:
        raise HTTPException(404, "Персонаж не найден")

    char.views = int(getattr(char, "views", 0) or 0) + 1
    db.commit()
    db.refresh(char)
    return _to_full_response(char, current_user.id)


# ─── Создать персонажа ────────────────────────────────────────────────────────
@router.post("/", response_model=schemas.CharacterResponse)
def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    new_char = models.Character(
        owner_id=current_user.id,
        name=character.name,
        persona=character.persona,
        description=character.description,
        greeting=character.greeting,
        avatar_url=character.avatar_url,
        tags=_join_tags(character.tags),
        is_public=character.is_public,
        model_id=character.model_id,
        is_nsfw=character.is_nsfw,
    )
    db.add(new_char)
    db.commit()
    db.refresh(new_char)
    return _to_full_response(new_char, current_user.id)


# ─── Редактировать персонажа (только владелец) ────────────────────────────────
@router.put("/{character_id}", response_model=schemas.CharacterResponse)
def update_character(
    character_id: int,
    data: schemas.CharacterUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    char = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.owner_id == current_user.id,
    ).first()
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


# ─── Удалить персонажа ────────────────────────────────────────────────────────
@router.delete("/{character_id}")
def delete_character(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    char = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.owner_id == current_user.id,
    ).first()
    if not char:
        raise HTTPException(404, "Персонаж не найден")
    db.delete(char)
    db.commit()
    return {"message": "Удалён"}


# ─── Лайк ──────────────────────────────────────────────────────────────────────
@router.post("/{character_id}/like")
def like_character(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    char = db.query(models.Character).filter(
        models.Character.id == character_id,
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True),
    ).first()
    if not char:
        raise HTTPException(404, "Персонаж не найден")

    existing = db.query(models.CharacterLike).filter(
        models.CharacterLike.user_id == current_user.id,
        models.CharacterLike.character_id == character_id,
    ).first()

    if existing:
        return {"liked": True, "like_count": int(getattr(char, "like_count", 0) or 0)}

    like = models.CharacterLike(user_id=current_user.id, character_id=character_id)
    db.add(like)
    char.like_count = int(getattr(char, "like_count", 0) or 0) + 1
    db.commit()
    db.refresh(char)
    return {"liked": True, "like_count": int(getattr(char, "like_count", 0) or 0)}


# ─── Снять лайк ────────────────────────────────────────────────────────────────
@router.delete("/{character_id}/like")
def unlike_character(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    char = db.query(models.Character).filter(models.Character.id == character_id).first()
    existing = db.query(models.CharacterLike).filter(
        models.CharacterLike.user_id == current_user.id,
        models.CharacterLike.character_id == character_id,
    ).first()

    if existing:
        db.delete(existing)
        if char:
            char.like_count = max(0, int(getattr(char, "like_count", 0) or 0) - 1)
        db.commit()
        db.refresh(char) if char else None

    return {"liked": False, "like_count": int(getattr(char, "like_count", 0) or 0) if char else 0}
