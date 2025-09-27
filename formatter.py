# perfume-bot/formatter.py
# Форматирование текста ответов.

import urllib.parse
from i18n import get_message # <-- Import i18n

def welcome_text(lang="ru"): # <-- Добавлен lang
    # Используем локализованный приветственный текст
    return get_message("welcome", lang)

def create_search_link(brand, name):
    """
    Создает URL для поиска Google по заданным бренду и названию.
    Текст запроса остается на русском, т.к. поиск "купить" в русской части Google
    даст более релевантные результаты для большинства пользователей.
    """
    query = f"купить {brand} {name} онлайн"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"

def format_response(original, copies, lang="ru"): # <-- Добавлен lang
    lines = []
    
    # Получаем локализованный префикс для ссылки [купить]/[buy]
    search_link_text = get_message("response_search_link_prefix", lang)
    
    # Форматируем оригинал
    original_link = create_search_link(original['brand'], original['name'])
    
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
            copy_link = create_search_link(brand, name)
            
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