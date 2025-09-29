import os
import sys
from datetime import datetime
from database import get_connection
from dotenv import load_dotenv

load_dotenv()

# Принимает необязательный user_id для отслеживания
def run_analytics(user_id_to_track=None):
    print("=============================================================")
    print("         ✨ РАСШИРЕННАЯ АНАЛИТИКА PERFUME BOT ✨")
    print("=============================================================")
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # ----------------------------------------------------
        # 1. Сводка по базе данных и пользователям (без изменений)
        # ----------------------------------------------------
        print("\n--- 1. СВОДКА ПО БАЗЕ ДАННЫХ И ПОЛЬЗОВАТЕЛЯМ ---")
        
        # ... (Код из раздела 1 остается без изменений) ...
        cur.execute("SELECT COUNT(*) FROM OriginalPerfume")
        print(f"✅ Общее количество оригиналов: {cur.fetchone()[0]}")

        cur.execute("SELECT COUNT(*) FROM CopyPerfume")
        print(f"✅ Общее количество клонов: {cur.fetchone()[0]}")

        cur.execute("SELECT COUNT(*) FROM UserMessages")
        total_messages = cur.fetchone()[0]
        print(f"✅ Общее количество сообщений (логом): {total_messages}")

        cur.execute("SELECT COUNT(DISTINCT user_id) FROM UserMessages")
        unique_users = cur.fetchone()[0]
        print(f"✅ Уникальных пользователей: {unique_users}")
        
        # ----------------------------------------------------
        # 2. Популярность (По числу клонов) (без изменений)
        # ----------------------------------------------------
        print("\n--- 2. САМЫЕ ПОПУЛЯРНЫЕ ОРИГИНАЛЫ (ПО ЧИСЛУ КЛОНОВ) ---")
        
        # ... (Код из раздела 2 остается без изменений) ...
        cur.execute("""
            SELECT 
                o.brand, 
                o.name, 
                COUNT(c.id) AS num_clones
            FROM OriginalPerfume o
            JOIN CopyPerfume c ON o.id = c.original_id
            GROUP BY o.id, o.brand, o.name
            ORDER BY num_clones DESC
            LIMIT 10
        """)
        popular_by_clone = cur.fetchall()

        for i, row in enumerate(popular_by_clone):
            print(f"  {i+1}. {row['brand']} - {row['name']} | Клонов: {row['num_clones']}")

        # ----------------------------------------------------
        # 3. Экономия (без изменений)
        # ----------------------------------------------------
        print("\n--- 3. ТОП-5 КЛОНОВ С НАИБОЛЬШЕЙ ЭКОНОМИЕЙ (saved_amount) ---")
        
        # ... (Код из раздела 3 остается без изменений) ...
        cur.execute("""
            SELECT 
                c.brand, 
                c.name, 
                c.saved_amount, 
                o.brand AS original_brand, 
                o.name AS original_name
            FROM CopyPerfume c
            JOIN OriginalPerfume o ON c.original_id = o.id
            WHERE c.saved_amount IS NOT NULL
            ORDER BY c.saved_amount DESC NULLS LAST 
            LIMIT 5
        """)
        top_savings = cur.fetchall()

        if top_savings:
            for i, row in enumerate(top_savings):
                saved_amount = f"{row['saved_amount']:.2f}%" if row['saved_amount'] is not None else "Нет данных"
                print(f"  {i+1}. {row['brand']} {row['name']} -> {row['original_brand']} {row['original_name']} | Экономия: {saved_amount}")
        else:
            print("Нет данных об экономии (saved_amount).")

        # ----------------------------------------------------
        # 4. Самые искомые парфюмы (без изменений)
        # ----------------------------------------------------
        print("\n--- 4. САМЫЕ ИСКОМЫЕ ПАРФЮМЫ (ТОП-10 УСПЕШНЫХ ЗАПРОСОВ) ---")
        
        # ... (Код из раздела 4 остается без изменений) ...
        cur.execute("""
            SELECT 
                TRIM(SUBSTRING(notes FROM 'Found: (.*)')) AS found_perfume, 
                COUNT(*) AS success_count
            FROM UserMessages
            WHERE status = 'success' AND notes LIKE 'Found: %%'
            GROUP BY found_perfume
            ORDER BY success_count DESC
            LIMIT 10
        """)
        top_searched = cur.fetchall()
        
        for i, row in enumerate(top_searched):
            perfume_name = row['found_perfume'].split(' | NOTE: ')[0] 
            print(f"  {i+1}. {perfume_name} | Успешных поисков: {row['success_count']}")

        # ----------------------------------------------------
        # 5. Сообщения с ошибкой (без изменений)
        # ----------------------------------------------------
        print("\n--- 5. ТОП-10 НЕУСПЕШНЫХ ЗАПРОСОВ (Для добавления в базу) ---")
        
        # ... (Код из раздела 5 остается без изменений) ...
        cur.execute("""
            SELECT 
                message, 
                COUNT(*) AS fail_count,
                MAX(notes) AS last_note
            FROM UserMessages
            WHERE status = 'fail' AND message NOT IN ('/start')
            GROUP BY message
            ORDER BY fail_count DESC
            LIMIT 10
        """)
        top_fails = cur.fetchall()
        
        for i, row in enumerate(top_fails):
            msg_preview = row['message'][:50] + '...' if len(row['message']) > 50 else row['message']
            print(f"  {i+1}. '{msg_preview}' | Ошибок: {row['fail_count']} | Причина: {row['last_note']}")

        # ----------------------------------------------------
        # 6. Активность пользователей (без изменений)
        # ----------------------------------------------------
        print("\n--- 6. ТОП-5 САМЫХ АКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ (Предпочтения) ---")
        
        # ... (Код из раздела 6 остается без изменений) ...
        cur.execute("""
            SELECT 
                user_id, 
                COUNT(*) AS total_msgs,
                MAX(timestamp) AS last_activity
            FROM UserMessages
            GROUP BY user_id
            ORDER BY total_msgs DESC
            LIMIT 5
        """)
        top_users = cur.fetchall()

        for i, row in enumerate(top_users):
            last_active_dt = row['last_activity'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {i+1}. User ID: {row['user_id']} | Сообщений: {row['total_msgs']} | Последняя активность: {last_active_dt}")

        # ====================================================
        # НОВЫЙ РАЗДЕЛ (УСЛОВНОЕ ОТСЛЕЖИВАНИЕ ПОЛЬЗОВАТЕЛЯ)
        # ====================================================
        if user_id_to_track is not None:
            
            # --- Защита от SQL-инъекций: 
            # В Python при работе с psycopg2 используйте placeholders (%s) и 
            # передавайте user_id вторым аргументом в cur.execute
            
            print(f"\n=============================================================")
            print(f"     🕵️‍♂️ АНАЛИТИКА ПОВЕДЕНИЯ ПОЛЬЗОВАТЕЛЯ ID: {user_id_to_track} 🕵️‍♂️")
            print(f"=============================================================")
            
            # 7. Все успешные запросы пользователя
            print("\n--- 7.1. УСПЕШНЫЕ ЗАПРОСЫ ПОЛЬЗОВАТЕЛЯ ---")
            cur.execute("""
                SELECT 
                    TRIM(SUBSTRING(notes FROM 'Found: (.*)')) AS found_perfume, 
                    COUNT(*) AS success_count,
                    MAX(timestamp) AS last_search
                FROM UserMessages
                WHERE status = 'success' AND notes LIKE 'Found: %%' AND user_id = %s
                GROUP BY found_perfume
                ORDER BY success_count DESC
            """, (user_id_to_track,))
            user_success = cur.fetchall()

            if user_success:
                for i, row in enumerate(user_success):
                    perfume_name = row['found_perfume'].split(' | NOTE: ')[0]
                    last_search_dt = row['last_search'].strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  {i+1}. {perfume_name} | Поисков: {row['success_count']} | Последний: {last_search_dt}")
            else:
                print("Нет успешных запросов от этого пользователя.")

            # 8. Все неуспешные запросы пользователя
            print("\n--- 7.2. НЕУСПЕШНЫЕ ЗАПРОСЫ ПОЛЬЗОВАТЕЛЯ ---")
            cur.execute("""
                SELECT 
                    message, 
                    COUNT(*) AS fail_count,
                    MAX(notes) AS last_note,
                    MAX(timestamp) AS last_fail
                FROM UserMessages
                WHERE status = 'fail' AND message NOT IN ('/start') AND user_id = %s
                GROUP BY message
                ORDER BY fail_count DESC
            """, (user_id_to_track,))
            user_fails = cur.fetchall()

            if user_fails:
                for i, row in enumerate(user_fails):
                    msg_preview = row['message'][:50] + '...' if len(row['message']) > 50 else row['message']
                    last_fail_dt = row['last_fail'].strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  {i+1}. '{msg_preview}' | Ошибок: {row['fail_count']} | Причина: {row['last_note']} | Последний: {last_fail_dt}")
            else:
                print("Нет неуспешных запросов от этого пользователя.")
        
        # ====================================================

    except Exception as e:
        print(f"\n❌ Произошла ошибка во время выполнения аналитики: {e}")
        print("💡 Убедитесь, что переменная среды **DATABASE_URL** корректно настроена и база данных доступна.")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
        print("\n=============================================================")
        print("          ✨ АНАЛИТИКА ЗАВЕРШЕНА ✨")
        print("=============================================================")

if __name__ == '__main__':
    # Проверяем, был ли передан ID пользователя как аргумент командной строки
    if len(sys.argv) > 1:
        try:
            # Пытаемся получить и преобразовать ID
            user_id = int(sys.argv[1])
            run_analytics(user_id_to_track=user_id)
        except ValueError:
            print(f"❌ Ошибка: '{sys.argv[1]}' не является корректным ID пользователя (целым числом).")
            sys.exit(1)
    else:
        # Запускаем обычную аналитику
        run_analytics()
