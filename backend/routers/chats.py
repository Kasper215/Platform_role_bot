# pylint: skip-file
# type: ignore

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database
import models
import schemas
import auth
from llm_client import get_bot_reply  # ← ИСПРАВЛЕНО

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/{character_id}", response_model=schemas.ChatResponse)
def create_or_get_chat(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    character = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.owner_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(404, "Персонаж не найден")
    
    chat_id = f"{current_user.id}_{character_id}"
    
    messages = db.query(models.Message).filter(
        models.Message.chat_id == chat_id,
        models.Message.user_id == current_user.id,
        models.Message.character_id == character_id
    ).order_by(models.Message.created_at).all()
    
    if len(messages) == 0 and character.greeting:
        greeting_msg = models.Message(
            chat_id=chat_id,
            user_id=current_user.id,
            character_id=character_id,
            role="assistant",
            content=str(character.greeting)
        )
        db.add(greeting_msg)
        db.commit()
        db.refresh(greeting_msg)
        messages = [greeting_msg]
    
    message_responses = []
    for m in messages:
        message_responses.append(schemas.MessageResponse(
            id=int(m.id),
            chat_id=str(m.chat_id),
            user_id=int(m.user_id),
            character_id=int(m.character_id),
            role=str(m.role),
            content=str(m.content),
            created_at=m.created_at
        ))
    
    return schemas.ChatResponse(
        id=hash(chat_id),
        character_id=character_id,
        messages=message_responses
    )


@router.post("/{chat_id}/messages", response_model=schemas.MessageResponse)
async def send_message(
    chat_id: int,
    request: schemas.MessageCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    character_id = request.character_id
    
    character = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.owner_id == current_user.id
    ).first()
    
    if not character:
        raise HTTPException(404, "Персонаж не найден")
    
    full_chat_id = f"{current_user.id}_{character_id}"
    
    user_msg = models.Message(
        chat_id=full_chat_id,
        user_id=current_user.id,
        character_id=character_id,
        role="user",
        content=request.content
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    
    history_messages = db.query(models.Message).filter(
        models.Message.chat_id == full_chat_id,
        models.Message.user_id == current_user.id,
        models.Message.character_id == character_id
    ).order_by(models.Message.created_at).limit(20).all()
    
    history = [{"role": m.role, "content": m.content} for m in history_messages[:-1]]
    
    try:
        bot_reply_text = await get_bot_reply(
            system_prompt=str(character.persona),
            history=history,
            user_message=request.content,
            bot_name=str(character.name),
            is_nsfw=bool(character.is_nsfw)
        )
    except Exception as e:
        bot_reply_text = f"*Ошибка генерации ответа:* {str(e)}"
    
    bot_msg = models.Message(
        chat_id=full_chat_id,
        user_id=current_user.id,
        character_id=character_id,
        role="assistant",
        content=bot_reply_text
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)
    
    return schemas.MessageResponse(
        id=int(bot_msg.id),
        chat_id=str(bot_msg.chat_id),
        user_id=int(bot_msg.user_id),
        character_id=int(bot_msg.character_id),
        role=str(bot_msg.role),
        content=str(bot_msg.content),
        created_at=bot_msg.created_at
    )