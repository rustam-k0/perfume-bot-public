# perfume-bot/database.py
import os
import time
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection(db_url=DATABASE_URL):
    if not db_url:
        raise ConnectionError("DATABASE_URL не указан! Проверьте настройки Render.")
    conn = psycopg2.connect(db_url)
    conn.cursor_factory = psycopg2.extras.DictCursor
    return conn

def init_db_if_not_exists(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserMessages (
            id SERIAL PRIMARY KEY, user_id BIGINT NOT NULL, 
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL, message TEXT NOT NULL,
            status TEXT NOT NULL, notes TEXT )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OriginalPerfume (
            id TEXT PRIMARY KEY, brand TEXT, name TEXT,
            price_eur REAL, url TEXT )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CopyPerfume (
            id TEXT PRIMARY KEY, original_id TEXT, brand TEXT, name TEXT,
            price_eur REAL, url TEXT, notes TEXT, saved_amount REAL,
            FOREIGN KEY(original_id) REFERENCES OriginalPerfume(id) )""")
    conn.commit()

def _convert_dict_row(row):
    return dict(row) if row else None

def fetch_all_originals(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, brand, name FROM OriginalPerfume")
    return [_convert_dict_row(row) for row in cur.fetchall()]

def fetch_clones_for_search(conn):
    cur = conn.cursor()
    cur.execute("SELECT brand, name, original_id FROM CopyPerfume")
    return [_convert_dict_row(row) for row in cur.fetchall()]

def fetch_original_by_id(conn, original_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = %s",
        (original_id,),
    )
    return _convert_dict_row(cur.fetchone())

def get_copies_by_original_id(conn, original_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount FROM CopyPerfume WHERE original_id = %s",
        (original_id,),
    )
    return [_convert_dict_row(row) for row in cur.fetchall()]

def log_message(conn, user_id, message, status, notes=""):
    cursor = conn.cursor()
    current_time = time.time()
    cursor.execute(
        "INSERT INTO UserMessages (user_id, timestamp, message, status, notes) VALUES (%s, to_timestamp(%s), %s, %s, %s)",
        (user_id, current_time, message, status, notes),
    )
    conn.commit()

# --- НОВЫЕ ФУНКЦИИ ---

def fetch_user_history(conn, user_id: int, limit: int = 5):
    """Извлекает последние N уникальных успешных поисков пользователя."""
    cur = conn.cursor()
    query = """
        SELECT DISTINCT ON (notes) notes
        FROM UserMessages
        WHERE user_id = %s AND status = 'success' AND notes LIKE 'Found: %%'
        ORDER BY notes, timestamp DESC
        LIMIT %s
    """
    cur.execute(query, (user_id, limit))
    # Извлекаем только название парфюма из "notes"
    history = []
    for row in cur.fetchall():
        try:
            perfume = row['notes'].split('Found: ')[1].split(' | NOTE:')[0]
            history.append(perfume)
        except IndexError:
            continue
    return history


def fetch_popular_originals(conn, limit: int = 10):
    """Извлекает самые популярные оригиналы по количеству клонов."""
    cur = conn.cursor()
    query = """
        SELECT o.brand, o.name, COUNT(c.id) AS clone_count
        FROM OriginalPerfume o
        JOIN CopyPerfume c ON o.id = c.original_id
        GROUP BY o.id
        ORDER BY clone_count DESC
        LIMIT %s
    """
    cur.execute(query, (limit,))
    return cur.fetchall()


def fetch_random_original(conn):
    """Извлекает случайный оригинал из базы данных."""
    cur = conn.cursor()
    # TABLESAMPLE SYSTEM (1) может быть неточным, но очень быстрым.
    # ORDER BY RANDOM() медленнее на больших таблицах. Выбираем его для точности.
    cur.execute("SELECT id, brand, name FROM OriginalPerfume ORDER BY RANDOM() LIMIT 1")
    return _convert_dict_row(cur.fetchone())

