# search.py
# Логика поиска парфюмов: гибкий поиск с приоритетом точного совпадения и устойчивостью к ошибкам.

from rapidfuzz import fuzz
from rapidfuzz.fuzz import WRatio
from utils import normalize_for_match
from database import fetch_all_originals, fetch_clones_for_search, fetch_original_by_id
from i18n import get_message 

# Глобальные переменные каталога. Загружаются один раз при старте.
CATALOG = None
BRAND_MAP = None
NAME_MAP = None
CLONE_CATALOG = None

# --- Вспомогательная функция для фаззи-поиска ---

def _fuzzy_search_best(query_norm, catalog_list, key, min_score=90):
    """
    Выполняет фаззи-поиск по списку каталогов и возвращает
    наилучшее совпадение, если оно выше min_score.
    """
    best_score = min_score
    best_match = None
    
    # Используем WRatio, так как он более устойчив к разным длинами строк
    for item in catalog_list:
        score = WRatio(query_norm, item[key])
        if score > best_score:
            best_score = score
            best_match = item

    if best_match:
        return {"ok": True, "result": best_match}
    return {"ok": False, "message": "Not found"}


# --- Инициализация и загрузка каталога ---

def _load_catalog(conn):
    """
    Загрузка всех оригиналов и клонов в память и подготовка словарей для поиска.
    """
    global CATALOG, BRAND_MAP, NAME_MAP, CLONE_CATALOG

    # Загрузка оригиналов
    rows = fetch_all_originals(conn)
    catalog, brand_map, name_map = [], {}, {}
    for r in rows:
        item = {
            "id": r["id"],
            "brand": r["brand"] or "",
            "name": r["name"] or "",
            "brand_norm": normalize_for_match(r["brand"]),
            "name_norm": normalize_for_match(r["name"]),
            "display_norm": normalize_for_match(f"{r['brand']} {r['name']}"),
        }
        catalog.append(item)
        brand_map.setdefault(item["brand_norm"], []).append(item)
        name_map.setdefault(item["name_norm"], []).append(item)

    # Загрузка клонов для поиска (используем только необходимые поля)
    clone_rows = fetch_clones_for_search(conn)
    clone_catalog = []
    for r in clone_rows:
        item = {
            "brand": r["brand"] or "",
            "name": r["name"] or "",
            # Ключ, по которому будем искать
            "display_norm": normalize_for_match(f"{r['brand']} {r['name']}"),
            # Ссылка на оригинал
            "original_id": r["original_id"],
        }
        clone_catalog.append(item)
        
    CATALOG = catalog
    BRAND_MAP = brand_map
    NAME_MAP = name_map
    CLONE_CATALOG = clone_catalog
    
    print(f"✅ Каталог загружен в память. Оригиналов: {len(CATALOG)}, Клонов: {len(CLONE_CATALOG)}")


# --- ФУНКЦИЯ ПОИСКА ОРИГИНАЛА ПО КЛОНУ (НОВАЯ ФУНКЦИЯ) ---

def find_original_by_clone(conn, user_norm, lang="ru"):
    """
    Ищет оригинал по совпадению с названиями клонов в CLONE_CATALOG.
    Возвращает оригинал, к которому относится этот клон.
    """
    global CLONE_CATALOG
    
    if not CLONE_CATALOG:
        # Каталог не загружен
        return {"ok": False, "message": get_message("error_not_found", lang)}

    # Шаг 1: Ищем совпадение с названием клона (высокий порог 95)
    clone_match = _fuzzy_search_best(user_norm, CLONE_CATALOG, "display_norm", min_score=95)

    if clone_match["ok"]:
        original_id = clone_match["result"]["original_id"]
        
        # Получаем объект оригинала по найденному ID
        original = fetch_original_by_id(conn, original_id)
        
        # Локализованная заметка, предупреждающая пользователя, что он ввел клон
        note = get_message("note_found_by_clone", lang)
        
        return {"ok": True, "original": original, "note": note}

    # Если точного совпадения нет
    return {"ok": False, "message": get_message("error_not_found", lang)}


# --- ГЛАВНАЯ ФУНКЦИЯ ПОИСКА ---

def find_original(conn, user_query, lang="ru"):
    """
    Выполняет комплексный поиск по всем шагам.
    """
    global CATALOG
    
    # 1. Загрузка каталога, если он еще не загружен
    if CATALOG is None:
        _load_catalog(conn)
    
    # 2. Нормализация запроса
    user_norm = normalize_for_match(user_query)
    user_words = user_norm.split()

    if not user_norm:
        return {"ok": False, "message": get_message("error_empty_query", lang)}

    # ----------------------------------------------------
    # Шаг 1: Точный поиск (БРЕНД НАЗВАНИЕ) - min_score=100
    # ----------------------------------------------------
    exact_match = _fuzzy_search_best(user_norm, CATALOG, "display_norm", min_score=100)
    if exact_match["ok"]:
        return {"ok": True, "original": exact_match["result"]}

    # ----------------------------------------------------
    # Шаг 2: Обратный поиск (НАЗВАНИЕ БРЕНД) - min_score=95
    # ----------------------------------------------------
    # Меняем слова местами, чтобы поймать "Sauvage Dior"
    if len(user_words) >= 2:
        user_norm_reversed = " ".join(user_words[::-1])
        match_rev = _fuzzy_search_best(user_norm_reversed, CATALOG, "display_norm", min_score=95)
        if match_rev["ok"]:
            # Локализованная заметка о неточном совпадении
            note = get_message("note_fuzzy_match", lang) 
            return {"ok": True, "original": match_rev["result"], "note": note}

    # ----------------------------------------------------
    # Шаг 3: Поиск по названию (Name Only) - min_score=90
    # ----------------------------------------------------
    # Ищем совпадение только по имени (если бренд опущен или неточен)
    name_match = _fuzzy_search_best(user_norm, CATALOG, "name_norm", min_score=90)
    if name_match["ok"]:
        return {"ok": True, "original": name_match["result"]}

    # ----------------------------------------------------
    # Шаг 4: Поиск по клонам (НОВЫЙ КРИТИЧЕСКИ ВАЖНЫЙ ШАГ)
    # ----------------------------------------------------
    clone_search_result = find_original_by_clone(conn, user_norm, lang)
    if clone_search_result["ok"]: 
        return clone_search_result

    # ----------------------------------------------------
    # Шаг 5: Поиск по бренду (Brand Only) - min_score=90
    # ----------------------------------------------------
    # Выполняется последним, чтобы поймать запросы типа "Dior"
    brand_match = _fuzzy_search_best(user_norm, CATALOG, "brand_norm", min_score=90)
    if brand_match["ok"]:
        # Локализованное предупреждение о неполном запросе по бренду
        brand_name = brand_match['result']['brand']
        # Используем .format для подстановки названия бренда
        message = get_message("error_brand_only", lang).format(brand_name=brand_name)
        return {"ok": False, "message": message}

    # ----------------------------------------------------
    # Шаг 6: Общий Фаззи-поиск (Display Norm) - min_score=85
    # ----------------------------------------------------
    # Снижаем порог для фаззи-поиска, чтобы поймать опечатки.
    match = _fuzzy_search_best(user_norm, CATALOG, "display_norm", min_score=85)
    if match["ok"]:
        # Локализованная заметка о неточном совпадении
        note = get_message("note_fuzzy_match", lang)
        return {"ok": True, "original": match["result"], "note": note}

    # ----------------------------------------------------
    # Шаг 7: Полный провал
    # ----------------------------------------------------
    return {"ok": False, "message": get_message("error_not_found", lang)}