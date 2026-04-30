import sqlite3
import json
import uuid
import os
from datetime import datetime

DB_PATH = "bazi.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                name TEXT,
                gender TEXT,
                calendar TEXT,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                hour INTEGER,
                minute INTEGER,
                birth_city TEXT,
                annotations TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def save_client(data: dict) -> str:
    client_id = str(uuid.uuid4())
    annotations = "{}"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO clients (id, name, gender, calendar, year, month, day, hour, minute, birth_city, annotations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            client_id, 
            data.get('name', ''), 
            data.get('gender', ''), 
            data.get('calendar', '公曆'), 
            data.get('year', 1990), 
            data.get('month', 1), 
            data.get('day', 1), 
            data.get('hour', 12), 
            data.get('minute', 0), 
            data.get('birth_city', '香港'), 
            annotations
        ))
    return client_id

def get_client(client_id: str) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id=?", (client_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
    return None

def update_annotation(client_id: str, section_id: str, text: str) -> bool:
    client = get_client(client_id)
    if not client:
        return False
    
    annotations = json.loads(client['annotations'] or "{}")
    annotations[section_id] = text
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE clients SET annotations=? WHERE id=?", (json.dumps(annotations, ensure_ascii=False), client_id))
    return True

def search_clients(query: str = "") -> list:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if query:
            # Simple wildcard search on name
            search_term = f"%{query}%"
            cur.execute("SELECT id, name, gender, year, month, day, created_at FROM clients WHERE name LIKE ? ORDER BY created_at DESC", (search_term,))
        else:
            cur.execute("SELECT id, name, gender, year, month, day, created_at FROM clients ORDER BY created_at DESC")
        
        return [dict(row) for row in cur.fetchall()]

def delete_client(client_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM clients WHERE id=?", (client_id,))
        return cur.rowcount > 0
