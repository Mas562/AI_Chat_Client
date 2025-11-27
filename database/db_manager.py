import sqlite3
import json
from datetime import datetime
from config import Config


class DatabaseManager:
    def __init__(self):
        Config.init()
        self.conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Таблица чатов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model TEXT,
                system_prompt TEXT
            )
        """)

        # Таблица сообщений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
            )
        """)

        self.conn.commit()

    # === ЧАТЫ ===

    def create_chat(self, title: str = "Новый чат",
                    model: str = "", system_prompt: str = "") -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO chats (title, model, system_prompt) VALUES (?, ?, ?)",
            (title, model, system_prompt)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all_chats(self) -> list:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title, created_at, updated_at, model 
            FROM chats ORDER BY updated_at DESC
        """)
        return cursor.fetchall()

    def get_chat(self, chat_id: int) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "model": row[4],
                "system_prompt": row[5]
            }
        return None

    def update_chat_title(self, chat_id: int, title: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE chats SET title = ?, updated_at = ? WHERE id = ?",
            (title, datetime.now(), chat_id)
        )
        self.conn.commit()

    def delete_chat(self, chat_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        self.conn.commit()

    # === СООБЩЕНИЯ ===

    def add_message(self, chat_id: int, role: str, content: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content)
        )
        cursor.execute(
            "UPDATE chats SET updated_at = ? WHERE id = ?",
            (datetime.now(), chat_id)
        )
        self.conn.commit()

    def get_messages(self, chat_id: int) -> list:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT role, content, timestamp 
            FROM messages WHERE chat_id = ? ORDER BY timestamp
        """, (chat_id,))
        return [{"role": r[0], "content": r[1], "timestamp": r[2]}
                for r in cursor.fetchall()]

    def clear_messages(self, chat_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()