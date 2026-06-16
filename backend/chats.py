# pylint: skip-file
# type: ignore

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timezone
import database
import models
import schemas
import auth
import zlib
from llm_client import get_bot_reply

router = APIRouter(prefix="/chats", tags=["chats"])


def _chat_id_for(user_id: int, character_id: int) -> str:
    return f"{user_id}_{character_id}"


def _ensure_chat_meta(db: Session, user_id: int, character_id: int):
    full_chat_id = _chat_id_for(user_id, character_id)
    meta = db.query(models.ChatMeta).filter(
        models.ChatMeta.user_id == user_id,
        models.ChatMeta.character_id == character_id,
    ).first()
    now = datetime.now(timezone.utc)
    if not meta:
        meta = models.ChatMeta(
            user_id=user_id,
            character_id=character_id,
            chat_id=full_chat_id,
            last_message_at=now,
            pinned=False,
        )
        db.add(meta)
    else:
        meta.last_message_at = now
    return meta


# ─── Список чатов пользователя (для боковой панели) ───────────────────────────
@router.get("/", response_model=list[schemas.ChatListItem])
def list_chats(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    # Последнее сообщение в каждом чате
    last_msg_sub = (
        db.query(
            models.Message.character_id,
            models.Message.content.label("content"),
            models.Message.role.label("role"),
            models.Message.created_at.label("created_at"),
            func.row_number().over(
                partition_by=models.Message.character_id,
                order_by=desc(models.Message.created_at),
            ).label("rn"),
        )
        .filter(models.Message.user_id == current_user.id)
        .subquery()
    )

    rows = (
        db.query(
            models.ChatMeta,
            models.Character,
            last_msg_sub.c.content,
            last_msg_sub.c.role,
            last_msg_sub.c.created_at,
        )
        .join(models.Character, models.ChatMeta.character_id == models.Character.id)
        .outerjoin(last_msg_sub, models.ChatMeta.character_id == last_msg_sub.c.character_id)
        .filter(models.ChatMeta.user_id == current_user.id, last_msg_sub.c.rn == 1)
        .order_by(desc(models.ChatMeta.pinned), desc(models.ChatMeta.last_message_at))
        .all()
    )

    result = []
    for meta, char, content, role, created_at in rows:
        result.append(schemas.ChatListItem(
            character_id=char.id,
            chat_id=meta.chat_id,
            character_name=char.name,
            avatar_url=char.avatar_url,
            is_nsfw=char.is_nsfw,
            last_content=content,
            last_role=role,
            last_message_at=created_at or meta.last_message_at,
            pinned=bool(meta.pinned),
        ))
    return result


# ─── Создать или получить чат по персонажу ────────────────────────────────────
@router.post("/{character_id}", response_model=schemas.ChatResponse)
def create_or_get_chat(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    character = db.query(models.Character).filter(
        models.Character.id == character_id
    ).filter(
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True)
    ).first()

    if not character:
        raise HTTPException(404, "Персонаж не найден")

    chat_id = _chat_id_for(current_user.id, character_id)

    # Учитываем чат в счётчике и в meta (один раз)
    _ensure_chat_meta(db, current_user.id, character_id)
    existing_meta_count = db.query(models.ChatMeta).filter(
        models.ChatMeta.user_id == current_user.id,
        models.ChatMeta.character_id == character_id,
    ).count()
    if existing_meta_count == 1 and (getattr(character, "chat_count", 0) or 0) == 0:
        character.chat_count = int(getattr(character, "chat_count", 0) or 0) + 1

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

    db.commit()

    message_responses = [
        schemas.MessageResponse(
            id=int(m.id),
            chat_id=str(m.chat_id),
            user_id=int(m.user_id),
            character_id=int(m.character_id),
            role=str(m.role),
            content=str(m.content),
            created_at=m.created_at,
        )
        for m in messages
    ]

    return schemas.ChatResponse(
        id=zlib.adler32(chat_id.encode()),
        character_id=character_id,
        messages=message_responses
    )


# ─── Отправить сообщение (стриминг ответа) ────────────────────────────────────
@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: int,
    request: schemas.MessageCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    character_id = request.character_id

    character = db.query(models.Character).filter(
        models.Character.id == character_id
    ).filter(
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True)
    ).first()

    if not character:
        raise HTTPException(404, "Персонаж не найден")

    full_chat_id = _chat_id_for(current_user.id, character_id)

    # 1. Сохраняем сообщение пользователя
    user_msg = models.Message(
        chat_id=full_chat_id,
        user_id=current_user.id,
        character_id=character_id,
        role="user",
        content=request.content
    )
    db.add(user_msg)
    _ensure_chat_meta(db, current_user.id, character_id)
    db.commit()
    db.refresh(user_msg)

    # 2. История (последние 20, без только что сохранённого)
    history_messages = db.query(models.Message).filter(
        models.Message.chat_id == full_chat_id,
        models.Message.user_id == current_user.id,
        models.Message.character_id == character_id
    ).order_by(models.Message.created_at).limit(20).all()
    history = [{"role": m.role, "content": m.content} for m in history_messages[:-1]]

    # 3. Стрим генерации
    async def event_generator():
        bot_reply_text = ""
        try:
            async for chunk in get_bot_reply(
                system_prompt=str(character.persona),
                history=history,
                user_message=request.content,
                bot_name=str(character.name),
                is_nsfw=bool(character.is_nsfw),
            ):
                bot_reply_text += chunk
                yield chunk

            with database.SessionLocal() as db_session:
                bot_msg = models.Message(
                    chat_id=full_chat_id,
                    user_id=current_user.id,
                    character_id=character_id,
                    role="assistant",
                    content=bot_reply_text
                )
                db_session.add(bot_msg)
                db_session.commit()

        except Exception as e:
            error_reply = f"*Ошибка генерации ответа:* {str(e)}"
            yield error_reply
            with database.SessionLocal() as db_session:
                bot_msg = models.Message(
                    chat_id=full_chat_id,
                    user_id=current_user.id,
                    character_id=character_id,
                    role="assistant",
                    content=error_reply
                )
                db_session.add(bot_msg)
                db_session.commit()

    return StreamingResponse(event_generator(), media_type="text/plain")


# ─── Регенерация последнего ответа бота (стрим) ───────────────────────────────
@router.post("/{character_id}/regenerate")
async def regenerate_last_reply(
    character_id: int,
    swipe: bool = False,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    character = db.query(models.Character).filter(
        models.Character.id == character_id
    ).filter(
        (models.Character.owner_id == current_user.id) | (models.Character.is_public == True)
    ).first()
    if not character:
        raise HTTPException(404, "Персонаж не найден")

    full_chat_id = _chat_id_for(current_user.id, character_id)

    # Находим последнее сообщение бота и последнее сообщение пользователя перед ним
    recent = db.query(models.Message).filter(
        models.Message.chat_id == full_chat_id,
        models.Message.user_id == current_user.id,
        models.Message.character_id == character_id,
    ).order_by(desc(models.Message.created_at)).limit(2).all()

    if not recent:
        raise HTTPException(400, "Нечего регенерировать")

    last = recent[0]
    # Если последнее сообщение — бота, удаляем его и регенерим по предыдущему user-сообщению
    if last.role == "assistant":
        db.delete(last)
        db.commit()

    # Перечитываем историю
    history_messages = db.query(models.Message).filter(
        models.Message.chat_id == full_chat_id,
        models.Message.user_id == current_user.id,
        models.Message.character_id == character_id,
    ).order_by(models.Message.created_at).limit(20).all()

    if not history_messages:
        raise HTTPException(400, "Нечего регенерировать")

    last_user_msg = history_messages[-1]
    history = [{"role": m.role, "content": m.content} for m in history_messages[:-1]]

    async def event_generator():
        bot_reply_text = ""
        try:
            async for chunk in get_bot_reply(
                system_prompt=str(character.persona),
                history=history,
                user_message=last_user_msg.content,
                bot_name=str(character.name),
                is_nsfw=bool(character.is_nsfw),
                swipe=swipe,
            ):
                bot_reply_text += chunk
                yield chunk

            with database.SessionLocal() as db_session:
                bot_msg = models.Message(
                    chat_id=full_chat_id,
                    user_id=current_user.id,
                    character_id=character_id,
                    role="assistant",
                    content=bot_reply_text,
                )
                db_session.add(bot_msg)
                db_session.commit()
        except Exception as e:
            error_reply = f"*Ошибка генерации ответа:* {str(e)}"
            yield error_reply
            with database.SessionLocal() as db_session:
                bot_msg = models.Message(
                    chat_id=full_chat_id,
                    user_id=current_user.id,
                    character_id=character_id,
                    role="assistant",
                    content=error_reply,
                )
                db_session.add(bot_msg)
                db_session.commit()

    return StreamingResponse(event_generator(), media_type="text/plain")


# ─── Удалить конкретное сообщение (для редактирования своего сообщения) ───────
@router.delete("/message/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    msg = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.user_id == current_user.id,
    ).first()
    if not msg:
        raise HTTPException(404, "Сообщение не найдено")

    # Удаляем это сообщение и все более поздние в этом чате
    db.query(models.Message).filter(
        models.Message.chat_id == msg.chat_id,
        models.Message.user_id == current_user.id,
        models.Message.created_at >= msg.created_at,
    ).delete(synchronize_session=False)
    db.commit()
    return {"deleted": True}


# ─── Закрепить/открепить чат ──────────────────────────────────────────────────
@router.patch("/{character_id}/pin")
def toggle_pin(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    meta = db.query(models.ChatMeta).filter(
        models.ChatMeta.user_id == current_user.id,
        models.ChatMeta.character_id == character_id,
    ).first()
    if not meta:
        raise HTTPException(404, "Чат не найден")
    meta.pinned = not meta.pinned
    db.commit()
    db.refresh(meta)
    return {"pinned": bool(meta.pinned)}


# ─── Очистить всю историю чата ────────────────────────────────────────────────
@router.delete("/{character_id}/clear")
def clear_chat(
    character_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    full_chat_id = _chat_id_for(current_user.id, character_id)

    deleted = db.query(models.Message).filter(
        models.Message.chat_id == full_chat_id,
        models.Message.user_id == current_user.id,
        models.Message.character_id == character_id
    ).delete()

    db.commit()
    return {"deleted": deleted, "message": f"Удалено {deleted} сообщений"}
