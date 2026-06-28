import os
import uuid
import urllib.request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.character import Character
from app.models.chat import Message, ChatMeta

AVATARS_DIR = "app/static/avatars"
os.makedirs(AVATARS_DIR, exist_ok=True)

# Компактный список персонажей
ONLINE_CHARACTERS = [
    {
        "name": "Нейро",
        "persona": "Нейро — профессиональная кибербезопасница и хакер. Циничная, язвительная, использует сленг, ценит острый ум. Говорит кратко и по делу. Любит кофе и неон. Обращается на 'ты'.",
        "greeting": "*Слышен тихий гул серверов. Девушка перед монитором приподнимает бровь.* Ну привет. Надеюсь, ты по делу. Готов работать, напарник?",
        "image_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=400&h=400&fit=crop"
    },
    {
        "name": "Аларик",
        "persona": "Аларик — эльфийский следопыт. Спокойный, благородный, говорит неторопливо. Защищает лес. К людям относится со скепсисом.",
        "greeting": "*Из тени дубов появляется эльф с луком за плечом.* Приветствую, странник. Какая нужда привела тебя в наши леса?",
        "image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?q=80&w=400&h=400&fit=crop"
    },
    {
        "name": "Шерлок",
        "persona": "Шерлок — гениальный детектив. Рациональный, хладнокровный, подмечает детали. Высокомерен, скучает без сложных загадок.",
        "greeting": "*Мужчина в строгом пальто ухмыляется.* Вы явно принесли мне интересное дело. Рассказывайте быстрее.",
        "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?q=80&w=400&h=400&fit=crop"
    }
]

def download_avatar(url: str) -> str:
    try:
        filename = f"{uuid.uuid4().hex}.png"
        dest_path = os.path.join(AVATARS_DIR, filename)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(dest_path, "wb") as f:
                f.write(response.read())
        return f"/static/avatars/{filename}"
    except Exception as e:
        print(f"Ошибка аватара {url}: {e}")
    return "/static/avatars/default.png"

def run():
    db: Session = SessionLocal()
    
    # Решаем проблему с NOT NULL owner_id: проверяем наличие юзера
    owner = db.query(User).first()
    if not owner:
        print("Создаем системного администратора в качестве владельца...")
        owner = User(
            email="admin@itg-hq.ru",
            hashed_password="dummy_password_hash",
            is_active=True
        )
        db.add(owner)
        try:
            db.commit()
            db.refresh(owner)
        except Exception as e:
            db.rollback()
            print(f"Не удалось создать пользователя: {e}")
            db.close()
            return

    print("Начинаем автозаливку персонажей...")
    added_count = 0
    for char_data in ONLINE_CHARACTERS:
        name = char_data["name"]
        existing = db.query(Character).filter(Character.name == name).first()
        if existing:
            continue
            
        print(f"Загрузка аватара для {name}...")
        avatar_url = download_avatar(char_data["image_url"])
        
        new_char = Character(
            owner_id=owner.id,
            name=name,
            persona=char_data["persona"],
            greeting=char_data["greeting"],
            avatar_url=avatar_url,
            is_public=True,
            is_nsfw=False,
            chat_count=0
        )
        db.add(new_char)
        try:
            db.commit()
            added_count += 1
            print(f"-> Успешно добавлен персонаж: {name}")
        except Exception as e:
            db.rollback()
            print(f"Ошибка сохранения {name}: {e}")
            
    db.close()
    print(f"Готово! Успешно залито персонажей: {added_count}")

if __name__ == "__main__":
    run()
