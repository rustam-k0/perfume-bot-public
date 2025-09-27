# perfume-bot/formatter.py
import urllib.parse
from i18n import get_message 

def welcome_text(lang="ru"): 
    return get_message("welcome", lang)

def create_search_link(brand, name, lang="ru"):
    """Создает URL для поиска Google, используя локализованное слово "купить"."""
    buy_word = get_message("search_query_buy_word", lang)
    query = f"{buy_word} {brand} {name} online"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"

def format_response(original, copies, lang="ru"): 
    lines = []
    
    search_link_text = get_message("response_search_link_prefix", lang)
    original_link = create_search_link(original['brand'], original['name'], lang)
    
    original_brand = original['brand'] if original['brand'] else ''
    original_name = original['name'] if original['name'] else ''
    
    lines.append(f"**{original_brand} {original_name}** [{search_link_text}]({original_link})")
    lines.append("---------------------")

    if not copies:
        lines.append(get_message("response_not_found_copies", lang))
    else:
        for c in copies:
            brand = c["brand"] if c["brand"] else ""
            name = c["name"] if c["name"] else ""
            copy_link = create_search_link(brand, name, lang)
            
            if brand and name:
                lines.append(f"▪️ {brand}: {name} [{search_link_text}]({copy_link})")
            elif name:
                lines.append(f"▪️ {name} [{search_link_text}]({copy_link})")
            elif brand:
                lines.append(f"▪️ {brand} [{search_link_text}]({copy_link})")
            
            # Добавление информации о цене и сбережениях (если они есть)
            if c.get('price_eur') is not None and c.get('saved_amount') is not None:
                price_line = get_message("response_price_line", lang).format(
                    price=c['price_eur'], 
                    saved_amount=int(c['saved_amount'])
                )
                lines.append(f"  ({price_line})")
            
    lines.append("\n" + get_message("response_footer", lang))
    return "\n".join(lines)