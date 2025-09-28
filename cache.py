# perfume-bot/cache.py
from cachetools import cached, TTLCache
from database import fetch_popular_originals, fetch_user_history, get_connection

# Создаем кэш: максимум 100 записей, время жизни каждой - 1 час (3600 секунд)
# Это идеально для данных, которые не меняются слишком часто (например, топ популярных)
cache = TTLCache(maxsize=100, ttl=3600)

@cached(cache)
def get_cached_popular_perfumes(limit: int = 10):
    """
    Кэшированная функция для получения популярных парфюмов.
    Результат будет храниться в кэше 1 час.
    """
    print("CACHE MISS: Fetching popular perfumes from DB.")
    conn = get_connection()
    try:
        return fetch_popular_originals(conn, limit)
    finally:
        conn.close()


def get_cached_user_history(user_id: int):
    """
    Кэшированная функция для получения истории пользователя.
    Используем более короткий TTL (5 минут), так как история меняется чаще.
    """
    # Создаем специфичный для пользователя ключ для кэша
    cache_key = f"history_{user_id}"
    
    if cache_key in cache:
        print(f"CACHE HIT: Returning history for user {user_id}.")
        return cache[cache_key]
    
    print(f"CACHE MISS: Fetching history for user {user_id} from DB.")
    conn = get_connection()
    try:
        history = fetch_user_history(conn, user_id)
        # Кэшируем результат на 5 минут (300 секунд)
        cache.setdefault(cache_key, history)
        # Устанавливаем TTL для этого конкретного ключа
        cache.expire_time[cache_key] = cache.currtime + 300
        return history
    finally:
        conn.close()