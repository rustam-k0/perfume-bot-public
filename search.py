from rapidfuzz import fuzz
from rapidfuzz.fuzz import WRatio
from utils import normalize_for_match
from database import fetch_all_originals, fetch_clones_for_search, fetch_original_by_id
from i18n import get_message 

CATALOG = None
BRAND_MAP = None
NAME_MAP = None
CLONE_CATALOG = None

def _load_catalog(conn):
    """
    """
    global CATALOG, BRAND_MAP, NAME_MAP, CLONE_CATALOG

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

    clone_rows = fetch_clones_for_search(conn)
    clone_catalog = []
    for r in clone_rows:
        item = {
            "brand": r["brand"] or "",
            "name": r["name"] or "",
            "display_norm": normalize_for_match(f"{r['brand']} {r['name']}"),
            "original_id": r["original_id"],
        }
        clone_catalog.append(item)

    CATALOG = catalog
    BRAND_MAP = brand_map
    NAME_MAP = name_map
    CLONE_CATALOG = clone_catalog

def init_catalog(conn):
    """"""
    _load_catalog(conn)

def _fuzzy_search_best(user_norm, search_space, target_key, min_score=90):
    """
    """
    best_match, score = None, 0
    
    for item in search_space:
        if item[target_key] == user_norm:
            return {"ok": True, "result": item}

    for item in search_space:
        s = WRatio(user_norm, item[target_key])
        if s > score:
            best_match, score = item, s
            
    if best_match and score >= min_score:
        return {"ok": True, "result": best_match}
    
    return {"ok": False, "result": None}

def find_original_by_clone(conn, user_norm, lang="ru"):
    """"""
    search_result = _fuzzy_search_best(user_norm, CLONE_CATALOG, "display_norm", min_score=80)
    
    if search_result["ok"]:
        found_clone = search_result["result"]
        original_data = fetch_original_by_id(conn, found_clone["original_id"])
        
        if original_data:
            original_item = {
                "id": original_data["id"],
                "brand": original_data["brand"],
                "name": original_data["name"],
                "brand_norm": normalize_for_match(original_data["brand"]),
                "name_norm": normalize_for_match(original_data["name"]),
                "display_norm": normalize_for_match(f"{original_data['brand']} {original_data['name']}"),
            }
            return {"ok": True, "original": original_item}
    
    return {"ok": False, "message": get_message("error_not_found", lang)}


def find_original(conn, user_text, lang="ru"):
    """
    """
    global CATALOG
    
    if not user_text or not user_text.strip():
        return {"ok": False, "message": get_message("error_empty_query", lang)}

    if not CATALOG:
        init_catalog(conn)

    user_norm = normalize_for_match(user_text)
    user_words = user_norm.split()
    
    
    match = _fuzzy_search_best(user_norm, CATALOG, "display_norm", min_score=100)
    if match["ok"]:
        return {"ok": True, "original": match["result"]}

    
    user_norm_reversed = " ".join(user_words[::-1])
    
    match_rev = _fuzzy_search_best(user_norm_reversed, CATALOG, "display_norm", min_score=95)
    if match_rev["ok"]:
        note = get_message("note_fuzzy_match", lang) 
        return {"ok": True, "original": match_rev["result"], "note": note}

    
    name_match = _fuzzy_search_best(user_norm, CATALOG, "name_norm", min_score=90)
    if name_match["ok"]:
        return {"ok": True, "original": name_match["result"]}

    
    clone_search_result = find_original_by_clone(conn, user_norm, lang)
    if clone_search_result["ok"]:
        return clone_search_result

    
    brand_match = _fuzzy_search_best(user_norm, CATALOG, "brand_norm", min_score=90)
    if brand_match["ok"]:
        brand_name = brand_match['result']['brand']
        message = get_message("error_brand_only", lang).format(brand_name=brand_name)
        return {"ok": False, "message": message}

    
    match = _fuzzy_search_best(user_norm, CATALOG, "display_norm", min_score=85)
    if match["ok"]:
        note = get_message("note_fuzzy_match", lang)
        return {"ok": True, "original": match["result"], "note": note}
    
    
    return {"ok": False, "message": get_message("error_not_found", lang)}