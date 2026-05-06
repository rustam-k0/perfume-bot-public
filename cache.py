from cachetools import cached, TTLCache
from database import fetch_popular_originals, fetch_user_history, get_connection

cache = TTLCache(maxsize=100, ttl=3600)

@cached(cache)
def get_cached_popular_perfumes(limit: int = 10):
    """
    """
    print("CACHE MISS: Fetching popular perfumes from DB.")
    conn = get_connection()
    try:
        return fetch_popular_originals(conn, limit)
    finally:
        conn.close()


def get_cached_user_history(user_id: int):
    """
    """
    cache_key = f"history_{user_id}"
    
    if cache_key in cache:
        print(f"CACHE HIT: Returning history for user {user_id}.")
        return cache[cache_key]
    
    print(f"CACHE MISS: Fetching history for user {user_id} from DB.")
    conn = get_connection()
    try:
        history = fetch_user_history(conn, user_id)
        cache.setdefault(cache_key, history)
        cache.expire_time[cache_key] = cache.currtime + 300
        return history
    finally:
        conn.close()