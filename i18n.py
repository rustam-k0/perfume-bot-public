# i18n.py
DEFAULT_LANG = "ru"

# Словари с текстами для разных языков
MESSAGES = {
    "ru": {
        "welcome": (
            "Привет! Я бот для поиска оригинальных ароматов и их популярных аналогов (дупов). "
            "Я помогу найти **самую выгодную замену** твоему любимому парфюму. "
            "\n\n**1. Выбери язык.**"
        ),
        "prompt_search": (
            "Отлично! Теперь **введи название оригинального парфюма и бренд** (например, *Dior Sauvage*)."
        ),
        "button_start": "Начать поиск!",
        "language_changed": "Язык изменен на **{lang_code}**! ✅",
        
        # --- Ошибки и предупреждения ---
        "error_empty_query": "Пожалуйста, введите название парфюма и бренд для поиска.",
        "error_not_found": "К сожалению, не удалось найти аромат по вашему запросу. Попробуйте ввести точное название.",
        "error_brand_only": "Найдено много ароматов бренда **{brand_name}**. Пожалуйста, добавьте название аромата.",
        
        # --- Результаты и форматирование ---
        "note_fuzzy_match": "Найдено по неточному совпадению. Проверьте правильность названия.",
        "note_found_by_clone": "Вы ввели название аналога. Результат показан для оригинального аромата.", # <--- НОВАЯ СТРОКА
        "response_note_prefix": "⚠️ *Предупреждение: *",
        "response_not_found_copies": "*Аналоги не найдены или не внесены в базу.*",
        "response_search_link_prefix": "🔍 Поиск",
        "response_price_line": "Цена: {price} € | Экономия: {saved_amount}%",
        "response_footer": "Нашли, что искали? Просто отправьте мне название другого аромата!",
        "search_query_buy_word": "купить",
        
        # --- Follow-up ---
        "followup_message": "Вы нашли, что искали? Может, хотите поискать другой аромат?",
        "followup_button": "Повторить поиск",
    },
    
    "en": {
        "welcome": (
            "Hi! I'm a bot designed to find original fragrances and their popular dupes (clones). "
            "I'll help you find the **best value replacement** for your favorite perfume. "
            "\n\n**1. Select your language.**"
        ),
        "prompt_search": (
            "Great! Now **enter the name of the original perfume and the brand** (e.g., *Dior Sauvage*)."
        ),
        "button_start": "Start searching!",
        "language_changed": "Language changed to **{lang_code}**! ✅",
        
        # --- Errors and warnings ---
        "error_empty_query": "Please enter the perfume name and brand to search.",
        "error_not_found": "Sorry, I couldn't find the fragrance you were looking for. Try entering the exact name.",
        "error_brand_only": "I found many fragrances from the brand **{brand_name}**. Please add the name of the fragrance.",
        
        # --- Results and formatting ---
        "note_fuzzy_match": "Found via fuzzy match. Please check the name for accuracy.",
        "note_found_by_clone": "You entered the name of a dupe. The result is shown for the original fragrance.", # <--- НОВАЯ СТРОКА
        "response_note_prefix": "⚠️ *Warning: *",
        "response_not_found_copies": "*No dupes found or they are not in our database.*",
        "response_search_link_prefix": "🔍 Search",
        "response_price_line": "Price: {price} € | Savings: {saved_amount}%",
        "response_footer": "Found what you needed? Just send me the name of another fragrance!",
        "search_query_buy_word": "buy",
        
        # --- Follow-up ---
        "followup_message": "Did you find what you were looking for? Maybe you want to search for another scent?",
        "followup_button": "Search again",
    }
}

def get_message(key, lang=DEFAULT_LANG):
    """Возвращает локализованное сообщение по ключу."""
    if lang not in MESSAGES:
        # Fallback to default language if selected language is not found
        lang = DEFAULT_LANG
    return MESSAGES[lang].get(key, MESSAGES[DEFAULT_LANG].get(key, f"MISSING_MESSAGE_KEY:{key}"))