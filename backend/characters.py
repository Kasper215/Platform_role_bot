from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import database
import models
import schemas
import auth

router = APIRouter(prefix="/characters", tags=["characters"])

@router.get("/", response_model=List[schemas.CharacterResponse])
def get_my_characters(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    characters = db.query(models.Character).filter(
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True)
    ).all()
    return characters

@router.post("/", response_model=schemas.CharacterResponse)
def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    new_char = models.Character(
        owner_id=current_user.id,
        name=character.name,
        persona=character.persona,
        greeting=character.greeting,
        avatar_url=character.avatar_url,
        is_public=character.is_public,
        model_id=character.model_id,
        is_nsfw=character.is_nsfw  # 🆕 ДОБАВИТЬ ЭТУ СТРОКУ
    )
    db.add(new_char)
    db.commit()
    db.refresh(new_char)
    return new_char

@router.delete("/{character_id}")
def delete_character(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    char = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.owner_id == current_user.id
    ).first()
    if not char:
        raise HTTPException(404, "Персонаж не найден")
    db.delete(char)
    db.commit()
    return {"message": "Удалён"}