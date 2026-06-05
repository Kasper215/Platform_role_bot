from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth, database

router = APIRouter(prefix="/bots", tags=["bots"])

@router.post("/", response_model=schemas.CharacterResponse)
def create_bot(
    bot: schemas.CharacterCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    new_bot = models.Character(**bot.model_dump(), owner_id=current_user.id)
    db.add(new_bot)
    db.commit()
    db.refresh(new_bot)
    return new_bot

@router.get("/", response_model=List[schemas.CharacterResponse])
def get_bots(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Возвращаем персонажей текущего пользователя и публичных персонажей
    bots = db.query(models.Character).filter(
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True)
    ).all()
    return bots

@router.get("/{bot_id}", response_model=schemas.CharacterResponse)
def get_bot(
    bot_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    bot = db.query(models.Character).filter(models.Character.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Character not found")
    if not bot.is_public and bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this character")
    return bot

@router.delete("/{bot_id}")
def delete_bot(
    bot_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    bot = db.query(models.Character).filter(models.Character.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Character not found")
    if bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this character")
    db.delete(bot)
    db.commit()
    return {"ok": True}
