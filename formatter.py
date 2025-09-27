# perfume-bot/formatter.py
# Форматирование текста ответов.

import urllib.parse
from i18n import get_message 

def welcome_text(lang="ru"): 
    # Используем локализованный приветственный текст
    return get_message("welcome", lang)

def create_search_link(brand, name, lang="ru"): # <-- Добавлен lang
    """
    Создает URL для поиска Google по заданным бренду и названию,
    используя локализованное слово "купить"/"buy".
    """
    # Получаем локализованное слово для поискового запроса
    buy_word = get_message("search_query_buy_word", lang)
    
    query = f"{buy_word} {brand} {name} online"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"

def format_response(original, copies, lang="ru"): 
    lines = []
    
    # Получаем локализованный префикс для ссылки
    search_link_text = get_message("response_search_link_prefix", lang)
    
    # Форматируем оригинал. Передаем lang для локализации поискового запроса.
    original_link = create_search_link(original['brand'], original['name'], lang)
    
    original_brand = original['brand'] if original['brand'] else ''
    original_name = original['name'] if original['name'] else ''
    
    lines.append(f"**{original_brand} {original_name}** [{search_link_text}]({original_link})")
    lines.append("---------------------")

    if not copies:
        # Локализованное сообщение "аналоги не найдены"
        lines.append(get_message("response_not_found_copies", lang))
    else:
        for c in copies:
            brand = c["brand"] if c["brand"] else ""
            name = c["name"] if c["name"] else ""
            # Передаем lang для локализации поискового запроса
            copy_link = create_search_link(brand, name, lang)
            
            # Условное форматирование для вывода названия и бренда
            if brand and name:
                lines.append(f"▪️ {brand}: {name} [{search_link_text}]({copy_link})")
            elif name:
                lines.append(f"▪️ {name} [{search_link_text}]({copy_link})")
            elif brand:
                lines.append(f"▪️ {brand} [{search_link_text}]({copy_link})")
            
    lines.append("---------------------")
    # Локализованное завершающее сообщение
    lines.append(get_message("response_close", lang))
    
    return "\n".join(lines)