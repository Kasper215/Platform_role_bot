"""
API-роутер: чаты и сообщения.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError  # <-- Добавили импорт для обработки ошибок уникальности
from datetime import datetime, timezone
import zlib

from app.core.database import get_db, SessionLocal
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.character import Character
from app.models.chat import Message, ChatMeta
from app.schemas.chat import (
    MessageCreate,
    MessageResponse,
    ChatResponse,
    ChatListItem,
)
from app.services.llm import get_bot_reply

router = APIRouter(prefix="/chats", tags=["chats"])


def _chat_id_for(user_id: int, character_id: int) -> str:
    return f"{user_id}_{character_id}"


@router.get("/", response_model=list[ChatListItem])
def list_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Список чатов пользователя (для боковой панели)."""
    last_msg_sub = (
        db.query(
            Message.character_id,
            Message.content.label("content"),
            Message.role.label("role"),
            Message.created_at.label("created_at"),
            func.row_number()
            .over(
                partition_by=Message.character_id,
                order_by=desc(Message.created_at),
            )
            .label("rn"),
        )
        .filter(Message.user_id == current_user.id)
        .subquery()
    )

    rows = (
        db.query(
            ChatMeta,
            Character,
            last_msg_sub.c.content,
            last_msg_sub.c.role,
            last_msg_sub.c.created_at,
        )
        .join(Character, ChatMeta.character_id == Character.id)
        .outerjoin(
            last_msg_sub, ChatMeta.character_id == last_msg_sub.c.character_id
        )
        .filter(ChatMeta.user_id == current_user.id, last_msg_sub.c.rn == 1)
        .order_by(
            desc(ChatMeta.pinned), desc(ChatMeta.last_message_at)
        )
        .all()
    )

    result = []
    for meta, char, content, role, created_at in rows:
        result.append(
            ChatListItem(
                character_id=char.id,
                chat_id=meta.chat_id,
                character_name=char.name,
                avatar_url=char.avatar_url,
                is_nsfw=char.is_nsfw,
                last_content=content,
                last_role=role,
                last_message_at=created_at or meta.last_message_at,
                pinned=bool(meta.pinned),
            )
        )
    return result


@router.post("/{character_id}", response_model=ChatResponse)
def create_or_get_chat(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Создать или получить существующий чат с персонажем."""
    # Проверяем персонажа
    character = (
        db.query(Character)
        .filter(Character.id == character_id)
        .filter(
            (Character.owner_id == current_user.id) | (Character.is_public == True)
        )
        .first()
    )
    if not character:
        raise HTTPException(404, "Персонаж не найден")

    # Проверяем существование чата
    meta = (
        db.query(ChatMeta)
        .filter(
            ChatMeta.user_id == current_user.id,
            ChatMeta.character_id == character_id,
        )
        .first()
    )

    if meta:
        # Если чат есть — используем его chat_id
        chat_id = meta.chat_id
        meta.last_message_at = datetime.now(timezone.utc)
        db.commit()
    else:
        # Если чата нет — пытаемся создать новый
        chat_id = _chat_id_for(current_user.id, character_id)
        meta = ChatMeta(
            user_id=current_user.id,
            character_id=character_id,
            chat_id=chat_id,
            last_message_at=datetime.now(timezone.utc),
        )
        db.add(meta)
        try:
            db.commit()
            db.refresh(meta)
            character.chat_count = int(character.chat_count or 0) + 1
            db.commit()
        except IntegrityError:
            # Обработка состояния гонки: если параллельный запрос успел записать meta первым
            db.rollback()
            meta = (
                db.query(ChatMeta)
                .filter(
                    ChatMeta.user_id == current_user.id,
                    ChatMeta.character_id == character_id,
                )
                .first()
            )
            if not meta:
                raise  # Пробрасываем ошибку дальше, если это не дублирование мета-информации
            chat_id = meta.chat_id

    # Получаем сообщения
    messages = (
        db.query(Message)
        .filter(
            Message.chat_id == chat_id,
            Message.user_id == current_user.id,
            Message.character_id == character_id,
        )
        .order_by(Message.created_at)
        .all()
    )

    # Если сообщений нет и есть приветствие — добавляем
    if len(messages) == 0 and character.greeting:
        greeting_msg = Message(
            chat_id=chat_id,
            user_id=current_user.id,
            character_id=character_id,
            role="assistant",
            content=str(character.greeting),
        )
        db.add(greeting_msg)
        db.commit()
        db.refresh(greeting_msg)
        messages = [greeting_msg]

    # Формируем ответ
    message_responses = [
        MessageResponse(
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

    return ChatResponse(
        id=zlib.adler32(chat_id.encode()),
        character_id=character_id,
        messages=message_responses,
    )


@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: int,
    request: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Отправить сообщение и получить стриминг ответа бота."""
    character_id = request.character_id

    character = (
        db.query(Character)
        .filter(Character.id == character_id)
        .filter(
            (Character.owner_id == current_user.id) | (Character.is_public == True)
        )
        .first()
    )
    if not character:
        raise HTTPException(404, "Персонаж не найден")

    full_chat_id = _chat_id_for(current_user.id, character_id)

    # Сохраняем сообщение пользователя
    user_msg = Message(
        chat_id=full_chat_id,
        user_id=current_user.id,
        character_id=character_id,
        role="user",
        content=request.content,
    )
    db.add(user_msg)

    # Обновляем мета-информацию о чате
    meta = (
        db.query(ChatMeta)
        .filter(
            ChatMeta.user_id == current_user.id,
            ChatMeta.character_id == character_id,
        )
        .first()
    )
    if not meta:
        meta = ChatMeta(
            user_id=current_user.id,
            character_id=character_id,
            chat_id=full_chat_id,
            last_message_at=datetime.now(timezone.utc),
        )
        db.add(meta)
    else:
        meta.last_message_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(user_msg)
    except IntegrityError:
        # Обработка аналогичного состояния гонки при отправке сообщений
        db.rollback()
        
        # Пересоздаем сущность сообщения пользователя, так как предыдущая транзакция сброшена
        user_msg = Message(
            chat_id=full_chat_id,
            user_id=current_user.id,
            character_id=character_id,
            role="user",
            content=request.content,
        )
        db.add(user_msg)
        
        # Заново получаем уже созданную другим потоком запись мета-информации
        meta = (
            db.query(ChatMeta)
            .filter(
                ChatMeta.user_id == current_user.id,
                ChatMeta.character_id == character_id,
            )
            .first()
        )
        if meta:
            meta.last_message_at = datetime.now(timezone.utc)
            
        db.commit()
        db.refresh(user_msg)

    # История (последние 20)
    history_messages = (
        db.query(Message)
        .filter(
            Message.chat_id == full_chat_id,
            Message.user_id == current_user.id,
            Message.character_id == character_id,
        )
        .order_by(Message.created_at)
        .limit(20)
        .all()
    )
    history = [
        {"role": m.role, "content": m.content} for m in history_messages[:-1]
    ]

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

            with SessionLocal() as db_session:
                bot_msg = Message(
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
            with SessionLocal() as db_session:
                bot_msg = Message(
                    chat_id=full_chat_id,
                    user_id=current_user.id,
                    character_id=character_id,
                    role="assistant",
                    content=error_reply,
                )
                db_session.add(bot_msg)
                db_session.commit()

    return StreamingResponse(event_generator(), media_type="text/plain")


@router.post("/{character_id}/regenerate")
async def regenerate_last_reply(
    character_id: int,
    swipe: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Регенерация последнего ответа бота (свайп)."""
    character = (
        db.query(Character)
        .filter(Character.id == character_id)
        .filter(
            (Character.owner_id == current_user.id) | (Character.is_public == True)
        )
        .first()
    )
    if not character:
        raise HTTPException(404, "Персонаж не найден")

    full_chat_id = _chat_id_for(current_user.id, character_id)

    recent = (
        db.query(Message)
        .filter(
            Message.chat_id == full_chat_id,
            Message.user_id == current_user.id,
            Message.character_id == character_id,
        )
        .order_by(desc(Message.created_at))
        .limit(2)
        .all()
    )

    if not recent:
        raise HTTPException(400, "Нечего регенерировать")

    last = recent[0]
    if last.role == "assistant":
        db.delete(last)
        db.commit()

    history_messages = (
        db.query(Message)
        .filter(
            Message.chat_id == full_chat_id,
            Message.user_id == current_user.id,
            Message.character_id == character_id,
        )
        .order_by(Message.created_at)
        .limit(20)
        .all()
    )

    if not history_messages:
        raise HTTPException(400, "Нечего регенерировать")

    last_user_msg = history_messages[-1]
    history = [
        {"role": m.role, "content": m.content} for m in history_messages[:-1]
    ]

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

            with SessionLocal() as db_session:
                bot_msg = Message(
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
            with SessionLocal() as db_session:
                bot_msg = Message(
                    chat_id=full_chat_id,
                    user_id=current_user.id,
                    character_id=character_id,
                    role="assistant",
                    content=error_reply,
                )
                db_session.add(bot_msg)
                db_session.commit()

    return StreamingResponse(event_generator(), media_type="text/plain")


@router.delete("/message/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Удалить сообщение и все последующие в чате."""
    msg = (
        db.query(Message)
        .filter(Message.id == message_id, Message.user_id == current_user.id)
        .first()
    )
    if not msg:
        raise HTTPException(404, "Сообщение не найдено")

    db.query(Message).filter(
        Message.chat_id == msg.chat_id,
        Message.user_id == current_user.id,
        Message.created_at >= msg.created_at,
    ).delete(synchronize_session=False)
    db.commit()
    return {"deleted": True}


@router.patch("/{character_id}/pin")
def toggle_pin(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Закрепить/открепить чат."""
    meta = (
        db.query(ChatMeta)
        .filter(
            ChatMeta.user_id == current_user.id,
            ChatMeta.character_id == character_id,
        )
        .first()
    )
    if not meta:
        raise HTTPException(404, "Чат не найден")
    meta.pinned = not meta.pinned
    db.commit()
    db.refresh(meta)
    return {"pinned": bool(meta.pinned)}


@router.delete("/{character_id}/clear")
def clear_chat(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Очистить всю историю чата."""
    full_chat_id = _chat_id_for(current_user.id, character_id)

    deleted = (
        db.query(Message)
        .filter(
            Message.chat_id == full_chat_id,
            Message.user_id == current_user.id,
            Message.character_id == character_id,
        )
        .delete()
    )

    db.commit()
    return {"deleted": deleted, "message": f"Удалено {deleted} сообщений"}