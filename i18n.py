# perfume-bot/i18n.py
# Централизованный словарь для всех локализованных строк.

# --- Настройка языка по умолчанию ---
DEFAULT_LANG = "ru"

MESSAGES = {
    "ru": {
        # --- ОБЩИЕ ---
        "button_lang_en": "English 🇬🇧",
        "button_lang_ru": "Русский 🇷🇺",
        "confirm_lang_set": "Язык изменен на Русский!",
        "go_back": "⬅️ Назад",

        # --- ГЛАВНОЕ МЕНЮ ---
        "menu_main_text": "👇 **Главное меню**\n\nВыберите, что вы хотите сделать:",
        "menu_search": "🔎 Найти парфюм",
        "menu_popular": "🌟 Популярные",
        "menu_random": "🎲 Случайный аромат",
        "menu_history": "📜 Моя история",
        
        # --- ПОИСК ---
        "search_prompt": "Отправьте мне сообщение в формате: **Бренд + Название**.\n\nНапример: Dior Sauvage.",
        "search_again": "🔎 Искать еще",

        # --- ПОПУЛЯРНЫЕ ---
        "popular_title": "🌟 **Топ-10 популярных ароматов**\n(по количеству аналогов)",

        # --- ИСТОРИЯ ---
        "history_title": "📜 **Ваша история 5 последних находок**",
        "history_empty": "Ваша история поиска пока пуста. Попробуйте найти что-нибудь!",
        
        # --- СЛУЧАЙНЫЙ АРОМАТ ---
        "random_title": "🎲 **Случайный аромат дня**",
        "random_again": "🎲 Еще один",

        # --- СООБЩЕНИЯ И ОШИБКИ ---
        "welcome": (
            "Привет👋 Я помогу найти доступные **аналоги** дорогого парфюма.\n\n"
            "Воспользуйтесь меню ниже для навигации."
        ),
        "error_empty_query": "Ой, я ничего не получил. Отправьте мне **бренд и название аромата**, пожалуйста.",
        "error_brand_only": "Кажется, вы указали только бренд **{brand_name}**. Пожалуйста, уточните название парфюма.",
        "error_not_found": "Увы, этот аромат пока мне не знаком. 😅 Пожалуйста, проверьте, правильно ли указаны бренд и название, или попробуйте другой.",
        "note_fuzzy_match": "Найдено по неточному совпадению. Проверьте результат.",
        "followup_text": "Круто! 🎉 Кажется, поиск сработал. Может, попробуем найти ещё один аромат?",
        
        # --- ФОРМАТТЕР ---
        "response_not_found_copies": (
            "Мне не удалось найти подходящие аналоги. Попробуйте ввести данные целиком (**Бренд + Название**) или поищите другой аромат. 😣"
        ),
        "response_search_link_prefix": "купить", 
        "response_close": "Надеюсь, информация была полезной! ✨",
        "response_note_prefix": "**🤖 Внимание:** ",
        "search_query_buy_word": "купить" 
    },
    
    "en": {
        # --- GENERAL ---
        "button_lang_en": "English 🇬🇧",
        "button_lang_ru": "Русский 🇷🇺",
        "confirm_lang_set": "Language switched to English!",
        "go_back": "⬅️ Back",

        # --- MAIN MENU ---
        "menu_main_text": "👇 **Main Menu**\n\nChoose what you want to do:",
        "menu_search": "🔎 Find Perfume",
        "menu_popular": "🌟 Popular",
        "menu_random": "🎲 Random Scent",
        "menu_history": "📜 My History",
        
        # --- SEARCH ---
        "search_prompt": "Send me a message in the format: **Brand + Name**.\n\nFor example: Dior Sauvage.",
        "search_again": "🔎 Search again",
        
        # --- POPULAR ---
        "popular_title": "🌟 **Top 10 Popular Perfumes**\n(by number of dupes)",

        # --- HISTORY ---
        "history_title": "📜 **Your 5 recent finds**",
        "history_empty": "Your search history is empty. Try to find something!",
        
        # --- RANDOM SCENT ---
        "random_title": "🎲 **Random Scent of the Day**",
        "random_again": "🎲 Another one",

        # --- MESSAGES & ERRORS ---
        "welcome": (
            "Hey there! 👋 I can help you find affordable **dupes** for expensive perfumes.\n\n"
            "Please use the menu below to navigate."
        ),
        "error_empty_query": "Oops, I didn't get anything. Please send me the **brand and name of the fragrance**.",
        "error_brand_only": "It looks like you only specified the brand **{brand_name}**. Please specify the perfume name.",
        "error_not_found": "Sorry, I don't know this fragrance yet. 😅 Please check that the brand and name are spelled correctly, or try another one.",
        "note_fuzzy_match": "Found via fuzzy match. Please check the result.",
        "followup_text": "Awesome! 🎉 It seems the search worked. Ready to try finding another perfume?",
        
        # --- FORMATTER ---
        "response_not_found_copies": (
            "I couldn't find any suitable dupes. Try entering the full details (**Brand + Name**) or search for a different fragrance. 😣"
        ),
        "response_search_link_prefix": "buy", 
        "response_close": "Hope the info was helpful! ✨",
        "response_note_prefix": "**🤖 Attention:** ",
        "search_query_buy_word": "buy"
    }
}

def get_message(key: str, lang: str = DEFAULT_LANG) -> str:
    """Извлекает локализованную строку, используя язык и ключ."""
    lang = lang.lower()
    if lang not in MESSAGES:
        lang = DEFAULT_LANG
    return MESSAGES[lang].get(key, f"MISSING_STRING_KEY_{key}")