# perfume-bot-public-RU/migrate.py
import sqlite3
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# --- Настройки DB (для безопасности используйте .env) ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("⚠️ WARNING: Using hardcoded URL from history. Add DATABASE_URL to your .env file.")
    DATABASE_URL = "postgresql://perfume_bot_public_posgresql_user:kIlMPx2gsC9uACxwMMk5KckZ4WaOsWit@dpg-d3c11k2li9vc73d6lee0-a.oregon-postgres.render.com/perfume_bot_public_posgresql"


def get_sqlite_connection(path="data/perfumes.db"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def get_postgres_connection(db_url):
    conn = psycopg2.connect(db_url)
    conn.cursor_factory = psycopg2.extras.DictCursor
    # Отключаем autocommit, чтобы вручную контролировать транзакции
    conn.autocommit = False 
    return conn

def migrate_data():
    try:
        sqlite_conn = get_sqlite_connection()
        postgres_conn = get_postgres_connection(DATABASE_URL)
        print("✅ Соединения с SQLite и PostgreSQL установлены.")
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return

    pg_cursor = postgres_conn.cursor()
    
    # 2. Очистка удаленных таблиц от тестовых данных (обязательно после rollback)
    try:
        # Удаляем клоны первыми из-за Foreign Key
        pg_cursor.execute("DELETE FROM copyperfume;")
        pg_cursor.execute("DELETE FROM originalperfume;")
        postgres_conn.commit() # Фиксируем очистку
        print("✅ Удаленные таблицы очищены от тестовых данных.")
    except Exception as e:
        print(f"❌ Ошибка при очистке таблиц: {e}")
        postgres_conn.rollback()
        return

    # 3. Миграция OriginalPerfume (879 строк)
    try:
        sl_cursor = sqlite_conn.cursor()
        sl_cursor.execute("SELECT id, brand, name, price_eur, url FROM OriginalPerfume;")
        originals_data = sl_cursor.fetchall()
        
        # Преобразование rows в список кортежей
        originals_list = [(r['id'], r['brand'], r['name'], r['price_eur'], r['url']) for r in originals_data]
        
        insert_query = """
        INSERT INTO originalperfume (id, brand, name, price_eur, url)
        VALUES (%s, %s, %s, %s, %s)
        """
        psycopg2.extras.execute_batch(pg_cursor, insert_query, originals_list)
        
        # КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: КОММИТИМ ОРИГИНАЛЫ СРАЗУ
        postgres_conn.commit() 
        
        print(f"✅ Успешно перенесено {len(originals_data)} строк в originalperfume.")
        
        # Создаем набор валидных original_id для фильтрации в следующем шаге
        valid_original_ids = {r['id'] for r in originals_data}
        
    except Exception as e:
        print(f"❌ Ошибка при миграции OriginalPerfume: {e}")
        postgres_conn.rollback() 
        return

    # 4. Миграция CopyPerfume (1416 строк)
    try:
        sl_cursor.execute("SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount FROM CopyPerfume;")
        copies_data = sl_cursor.fetchall()
        
        # --- ФИЛЬТРАЦИЯ ДАННЫХ И ПОДГОТОВКА К ВСТАВКЕ ---
        copies_to_insert = []
        skipped_count = 0
        
        for r in copies_data:
            # Проверка Foreign Key на стороне Python
            if r['original_id'] not in valid_original_ids:
                skipped_count += 1
                continue
                
            copies_to_insert.append((
                r['id'], r['original_id'], r['brand'], r['name'], r['price_eur'], 
                r['url'], r['notes'], r['saved_amount']
            ))

        insert_query = """
        INSERT INTO copyperfume (id, original_id, brand, name, price_eur, url, notes, saved_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Вставка отфильтрованного списка
        psycopg2.extras.execute_batch(pg_cursor, insert_query, copies_to_insert)
        
        # Коммит вставленных копий
        postgres_conn.commit()
        
        print(f"✅ Успешно перенесено {len(copies_to_insert)} строк в copyperfume.")
        if skipped_count > 0:
            print(f"⚠️ Пропущено {skipped_count} строк в CopyPerfume из-за отсутствия оригиналов в OriginalPerfume.")
            
    except Exception as e:
        print(f"❌ Ошибка при миграции CopyPerfume: {e}")
        # Если здесь будет ошибка, она откатит только последнюю транзакцию (CopyPerfume)
        postgres_conn.rollback() 
        return

    # 5. Завершение
    sqlite_conn.close()
    postgres_conn.close()
    print("✨ Миграция завершена! Базы данных закрыты.")

if __name__ == "__main__":
    migrate_data()