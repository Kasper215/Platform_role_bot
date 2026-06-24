import os
import base64
import json
import uuid
from PIL import Image
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.character import Character

# Папка, куда вы будете складывать скачанные PNG-карточки
CARDS_INPUT_DIR = "import_cards"
# Папка для сохранения очищенных аватарок в вашем проекте
AVATARS_DIR = "app/static/avatars"

os.makedirs(CARDS_INPUT_DIR, exist_ok=True)
os.makedirs(AVATARS_DIR, exist_ok=True)

def extract_tavern_metadata(png_path: str) -> dict | None:
    """Извлекает JSON-данные персонажа из PNG метаданных карточки Tavern."""
    try:
        with Image.open(png_path) as img:
            img.load()
            # Данные обычно лежат в tEXt/iTXt чанке с ключом "chara"
            raw_chara = img.info.get("chara")
            if not raw_chara:
                return None
            
            # Декодируем base64 (стандарт для Tavern V1/V2)
            decoded_bytes = base64.b64decode(raw_chara)
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
            return json.loads(decoded_str)
    except Exception as e:
        print(f"Ошибка при чтении {png_path}: {e}")
        return None

def save_avatar_from_card(png_path: str) -> str:
    """Сохраняет саму картинку карточки как квадратный аватар."""
    filename = f"{uuid.uuid4().hex}.png"
    dest_path = os.path.join(AVATARS_DIR, filename)
    
    with Image.open(png_path) as img:
        # Tavern карты обычно вертикальные, делаем их квадратными аватарами (crop/resize)
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2
        
        cropped = img.crop((left, top, right, bottom))
        cropped.thumbnail((400, 400), Image.Resampling.LANCZOS)
        cropped.save(dest_path, "PNG")
        
    return f"/static/avatars/{filename}"

def run_import():
    db: Session = SessionLocal()
    files = [f for f in os.listdir(CARDS_INPUT_DIR) if f.lower().endswith(".png")]
    
    if not files:
        print(f"Пожалуйста, положите PNG-карточки персонажей в папку {CARDS_INPUT_DIR}")
        return

    imported_count = 0
    for file in files:
        file_path = os.path.join(CARDS_INPUT_DIR, file)
        card_data = extract_tavern_metadata(file_path)
        
        if not card_data:
            print(f"Файл {file} не содержит метаданных Tavern. Пропускаем.")
            continue
        
        # Распаковываем стандартные поля (поддерживает форматы V1 и V2)
        # Если это формат V2, данные могут лежать внутри ключа "data"
        data = card_data.get("data", card_data)
        
        name = data.get("name") or data.get("char_name")
        persona = data.get("description") or data.get("char_persona", "")
        greeting = data.get("first_mes") or data.get("char_greeting", "")
        
        if not name:
            print(f"Не удалось найти имя персонажа в {file}. Пропускаем.")
            continue
            
        # Проверяем, нет ли его уже в базе
        existing = db.query(Character).filter(Character.name == name).first()
        if existing:
            print(f"Персонаж '{name}' уже есть в базе данных. Пропускаем.")
            continue

        try:
            avatar_url = save_avatar_from_card(file_path)
            
            new_char = Character(
                name=name,
                persona=persona,       # Системный промпт (описание личности)
                greeting=greeting,     # Приветственное сообщение
                avatar_url=avatar_url,
                is_public=True,
                is_nsfw=False,         # Можно настроить логику проверки по тегам
                chat_count=0
            )
            db.add(new_char)
            db.commit()
            imported_count += 1
            print(f"Успешно импортирован: {name}")
        except Exception as e:
            db.rollback()
            print(f"Ошибка при сохранении {name} в базу: {e}")
            
    db.close()
    print(f"Импорт завершен. Добавлено персонажей: {imported_count}")

if __name__ == "__main__":
    run_import()