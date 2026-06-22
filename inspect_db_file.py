import sqlite3
import json

def inspect():
    conn = sqlite3.connect('backend/roleplay.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    data = {"characters": [], "messages": []}
    
    c.execute("SELECT id, name, persona, greeting, is_nsfw, model_id FROM characters")
    for r in c.fetchall():
        data["characters"].append(dict(r))
        
    c.execute("SELECT id, chat_id, role, content, created_at FROM messages ORDER BY id DESC")
    for r in reversed(c.fetchall()):
        data["messages"].append(dict(r))
        
    with open("backend/db_inspection.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("Exported DB inspection to backend/db_inspection.json")

if __name__ == "__main__":
    inspect()
