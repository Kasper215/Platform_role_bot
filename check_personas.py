"""Quick script to inspect character personas for conflicting instructions."""
import sqlite3
import json

DB_PATH = "triumphroll.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, name, is_nsfw, persona, greeting FROM characters")
rows = cursor.fetchall()

results = []
for row in rows:
    results.append({
        "id": row["id"],
        "name": row["name"],
        "is_nsfw": row["is_nsfw"],
        "persona": row["persona"],
        "greeting": row["greeting"]
    })

with open("backend/personas_dump.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Saved {len(results)} characters to backend/personas_dump.json")
conn.close()
