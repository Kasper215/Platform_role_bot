"""Dump all messages for character_id=1 to see chat history."""
import sqlite3
import json

DB_PATH = "triumphroll.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT id, chat_id, user_id, character_id, role, content, created_at 
    FROM messages 
    WHERE character_id IN (1, 2)
    ORDER BY created_at DESC
    LIMIT 30
""")
rows = cursor.fetchall()

results = []
for row in rows:
    results.append({
        "id": row["id"],
        "chat_id": row["chat_id"],
        "character_id": row["character_id"],
        "role": row["role"],
        "content": row["content"],
        "created_at": str(row["created_at"])
    })

with open("backend/messages_dump.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Dumped {len(results)} messages")
conn.close()
