import sqlite3

def inspect():
    conn = sqlite3.connect('backend/triumphroll.db')
    c = conn.cursor()
    
    print("--- CHARACTERS ---")
    c.execute("SELECT id, name, persona, greeting, is_nsfw, model_id FROM characters")
    chars = c.fetchall()
    for char in chars:
        print(f"ID: {char[0]} | Name: {char[1]} | NSFW: {char[4]} | Model: {char[5]}")
        print(f"Persona: {char[2]}")
        print(f"Greeting: {char[3]}")
        print("-" * 40)
        
    print("\n--- RECENT MESSAGES ---")
    c.execute("SELECT id, chat_id, role, content, created_at FROM messages ORDER BY id DESC LIMIT 15")
    msgs = c.fetchall()
    for msg in reversed(msgs):
        print(f"ID: {msg[0]} | Chat: {msg[1]} | Role: {msg[2]}")
        print(f"Content: {msg[3]}")
        print("-" * 20)

if __name__ == "__main__":
    inspect()
