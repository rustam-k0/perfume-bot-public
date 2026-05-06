import os
import time
import sqlite3
from urllib.parse import urlparse
from dotenv import load_dotenv

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/perfumes.db")

def get_db_type():
    """Определяет тип базы данных на основе URL."""
    if "postgres" in DATABASE_URL:
        return "postgres"
    return "sqlite"

def get_connection(db_url=DATABASE_URL):
    if not db_url:
        db_url = "sqlite:///data/perfumes.db"
    
    if "postgres" in db_url:
        if not psycopg2:
            raise ImportError("psycopg2 не установлен, но указан Postgres URL")
        conn = psycopg2.connect(db_url)
        conn.cursor_factory = psycopg2.extras.DictCursor
        return conn
    else:
        db_path = db_url.replace("sqlite:///", "")
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  
        return conn

def _execute(cursor, query, params=None):
    """Адаптер для выполнения запросов (разный синтаксис плейсхолдеров)."""
    db_type = get_db_type()
    if params is None:
        params = ()
    
    if db_type == "sqlite":
        query = query.replace("%s", "?")
        query = query.replace("to_timestamp(?)", "?") 
        if "DISTINCT ON" in query:
            query = query.replace("DISTINCT ON (notes) notes", "notes")
    
    cursor.execute(query, params)
    return cursor

def init_db_if_not_exists(conn):
    cursor = conn.cursor()
    db_type = get_db_type()
    
    id_type = "SERIAL PRIMARY KEY" if db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    _execute(cursor, f"""
        CREATE TABLE IF NOT EXISTS UserMessages (
            id {id_type}, user_id BIGINT NOT NULL, 
            timestamp TIMESTAMP, message TEXT NOT NULL,
            status TEXT NOT NULL, notes TEXT )""") 
    _execute(cursor, """
        CREATE TABLE IF NOT EXISTS OriginalPerfume (
            id TEXT PRIMARY KEY, brand TEXT, name TEXT,
            price_eur REAL, url TEXT )""")
    _execute(cursor, """
        CREATE TABLE IF NOT EXISTS CopyPerfume (
            id TEXT PRIMARY KEY, original_id TEXT, brand TEXT, name TEXT,
            price_eur REAL, url TEXT, notes TEXT, saved_amount REAL,
            FOREIGN KEY(original_id) REFERENCES OriginalPerfume(id) )""")
    conn.commit()

def _convert_dict_row(row):
    return dict(row) if row else None

def fetch_all_originals(conn):
    cur = conn.cursor()
    _execute(cur, "SELECT id, brand, name FROM OriginalPerfume")
    return [_convert_dict_row(row) for row in cur.fetchall()]

def fetch_clones_for_search(conn):
    cur = conn.cursor()
    _execute(cur, "SELECT brand, name, original_id FROM CopyPerfume")
    return [_convert_dict_row(row) for row in cur.fetchall()]

def fetch_original_by_id(conn, original_id):
    cur = conn.cursor()
    _execute(cur, 
        "SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = %s",
        (original_id,)
    )
    return _convert_dict_row(cur.fetchone())

def get_copies_by_original_id(conn, original_id):
    cur = conn.cursor()
    _execute(cur,
        "SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount FROM CopyPerfume WHERE original_id = %s",
        (original_id,)
    )
    return [_convert_dict_row(row) for row in cur.fetchall()]

def log_message(conn, user_id, message, status, notes=""):
    cursor = conn.cursor()
    current_time = time.time()
    _execute(cursor,
        "INSERT INTO UserMessages (user_id, timestamp, message, status, notes) VALUES (%s, to_timestamp(%s), %s, %s, %s)",
        (user_id, current_time, message, status, notes),
    )
    conn.commit()

def fetch_user_history(conn, user_id: int, limit: int = 5):
    cur = conn.cursor()
    query = """
        SELECT notes, timestamp
        FROM UserMessages
        WHERE user_id = %s AND status = 'success' AND notes LIKE 'Found: %%'
        ORDER BY timestamp DESC
        LIMIT 20
    """
    _execute(cur, query, (user_id,))
    
    seen_perfumes = set()
    history = []
    
    for row in cur.fetchall():
        if len(history) >= limit:
            break
        try:
            perfume_note = row['notes']
            if perfume_note in seen_perfumes:
                continue
            
            perfume = perfume_note.split('Found: ')[1].split(' | NOTE:')[0]
            seen_perfumes.add(perfume_note)
            history.append(perfume)
        except (IndexError, AttributeError):
            continue
            
    return history

def fetch_popular_originals(conn, limit: int = 10):
    cur = conn.cursor()
    query = """
        SELECT o.brand, o.name, COUNT(c.id) AS clone_count
        FROM OriginalPerfume o
        JOIN CopyPerfume c ON o.id = c.original_id
        GROUP BY o.id, o.brand, o.name
        ORDER BY clone_count DESC
        LIMIT %s
    """
    _execute(cur, query, (limit,))
    return cur.fetchall()

def fetch_random_original(conn):
    cur = conn.cursor()
    _execute(cur, "SELECT id, brand, name FROM OriginalPerfume ORDER BY RANDOM() LIMIT 1")
    return _convert_dict_row(cur.fetchone())