# database.py
# Финальная версия для PostgreSQL

import os
import datetime # <--- НОВЫЙ ИМПОРТ
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Загружаем переменную окружения DATABASE_URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# --- ГЛАВНЫЕ ФУНКЦИИ БАЗЫ ДАННЫХ ---

def get_connection(db_url=DATABASE_URL):
    """
    Устанавливает соединение с PostgreSQL, используя URL из переменных окружения.
    """
    if not db_url:
        raise ConnectionError("DATABASE_URL не указан! Проверьте настройки Render.")
    
    # 1. Подключение к PostgreSQL по URL
    conn = psycopg2.connect(db_url)
    
    # 2. Настройка: DictCursor возвращает строки в виде словарей
    conn.cursor_factory = psycopg2.extras.DictCursor
    return conn

def init_db_if_not_exists(conn):
    """
    Инициализирует базу данных, создавая все необходимые таблицы.
    """
    cursor = conn.cursor()

    # Таблица для логов сообщений (UserMessages)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserMessages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL, 
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL, 
            notes TEXT
        )
    """)

    # Таблица оригиналов (OriginalPerfume)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OriginalPerfume (
            id TEXT PRIMARY KEY,
            brand TEXT NOT NULL,
            name TEXT NOT NULL,
            price_eur REAL,
            url TEXT
        )
    """)
    
    # Таблица клонов (CopyPerfume)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CopyPerfume (
            id TEXT PRIMARY KEY,
            original_id TEXT REFERENCES OriginalPerfume(id) ON DELETE CASCADE,
            brand TEXT NOT NULL,
            name TEXT NOT NULL,
            price_eur REAL,
            url TEXT,
            notes TEXT,
            saved_amount REAL
        )
    """)
    conn.commit()

def _convert_dict_row(row):
    """Преобразует psycopg2.extras.DictRow в стандартный dict."""
    return dict(row) if row else None

# --- ФУНКЦИИ ВЫБОРКИ ДАННЫХ (SELECT) ---

def fetch_all_originals(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, brand, name, price_eur, url FROM OriginalPerfume")
    return [_convert_dict_row(row) for row in cur.fetchall()]

def fetch_clones_for_search(conn):
    # Используется в search.py для загрузки каталога клонов
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

# --- ФУНКЦИЯ ЛОГИРОВАНИЯ (INSERT) ---

def log_message(conn, user_id, message, status, notes=""):
    """
    Логирует сообщение пользователя в таблицу UserMessages, используя datetime.
    """
    cursor = conn.cursor()
    # ИСПОЛЬЗУЕМ datetime.datetime.now()
    current_time = datetime.datetime.now()
    
    cursor.execute(
        """
        INSERT INTO UserMessages (user_id, timestamp, message, status, notes)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, current_time, message, status, notes)
    )
    conn.commit()