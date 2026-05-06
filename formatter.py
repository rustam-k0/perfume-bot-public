import urllib.parse
from i18n import get_message

def create_search_link(brand, name, lang="ru"):
    buy_word = get_message("search_query_buy_word", lang)
    query = f"{buy_word} {brand} {name} online"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"

def format_response(original, copies, lang="ru"):
    lines = []
    search_link_text = get_message("response_search_link_prefix", lang)

    original_link = create_search_link(original['brand'], original['name'], lang)
    original_brand = original['brand'] or ''
    original_name = original['name'] or ''

    lines.append(f"**{original_brand} {original_name}** [{search_link_text}]({original_link})")
    lines.append("---------------------")

    if not copies:
        lines.append(get_message("response_not_found_copies", lang))
    else:
        copies.sort(key=lambda c: c.get('saved_amount') if c.get('saved_amount') is not None else -1, reverse=True)

        for c in copies:
            brand = c.get("brand", "")
            name = c.get("name", "")
            saved_amount = c.get("saved_amount")
            copy_link = create_search_link(brand, name, lang)

            saving_text = ""
            if saved_amount is not None:
                saving_text = f" ({saved_amount:.0f}%)"

            if brand and name:
                lines.append(f"▪️ {brand}: {name}{saving_text} [{search_link_text}]({copy_link})")
            elif name:
                lines.append(f"▪️ {name}{saving_text} [{search_link_text}]({copy_link})")
            elif brand:
                lines.append(f"▪️ {brand}{saving_text} [{search_link_text}]({copy_link})")

    lines.append("---------------------")
    lines.append(get_message("response_close", lang))

    return "\n".join(lines)

def format_popular_list(popular_items: list, lang: str) -> str:
    lines = [f"{get_message('popular_title', lang)}\n"]
    for i, item in enumerate(popular_items, 1):
        lines.append(f"{i}. **{item['brand']} {item['name']}** ({item['clone_count']})")
    return "\n".join(lines)


def format_history_list(history_items: list, lang: str) -> str:
    lines = [f"{get_message('history_title', lang)}\n"]
    if not history_items:
        lines.append(get_message("history_empty", lang))
    else:
        for i, item in enumerate(history_items, 1):
            lines.append(f"{i}. {item}")
    return "\n".join(lines)