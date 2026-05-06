DEFAULT_LANG = "ru"

MESSAGES = {
    "ru": {
        "button_lang_en": "English 🇬🇧",
        "button_lang_ru": "Русский 🇷🇺",
        "confirm_lang_set": "Язык изменен на Русский!",
        "go_back": "⬅️ Назад",

        "menu_main_text": "👇 **Главное меню**\n\nВыберите, что вы хотите сделать:",
        "menu_search": "🔎 Найти парфюм",
        "menu_popular": "🌟 Популярные",
        "menu_random": "🎲 Случайный аромат",
        "menu_history": "📜 Моя история",

        "search_prompt": "Отправьте мне сообщение в формате: **Бренд + Название**.\n\nНапример: Dior Sauvage.",
        "search_again": "🔎 Искать еще",

        "popular_title": "🌟 **Топ-10 популярных ароматов**\n(по количеству аналогов)",

        "history_title": "📜 **Ваша история 5 последних находок**",
        "history_empty": "Ваша история поиска пока пуста. Попробуйте найти что-нибудь!",

        "random_title": "🎲 **Случайный аромат**",
        "random_again": "🎲 Еще один случайный",

        "welcome": (
            "Привет! 👋 Я помогу вам найти доступные **аналоги** дорогих парфюмов.\n\n"
            "Используйте меню ниже для навигации."
        ),
        "error_empty_query": "Ой, я ничего не получил. Пожалуйста, отправьте мне **бренд и название аромата**.",
        "error_brand_only": "Похоже, вы указали только бренд **{brand_name}**. Пожалуйста, уточните название парфюма.",
        "error_not_found": "Извините, я еще не знаю этот аромат. 😅 Проверьте правильность написания бренда и названия или попробуйте другой.",
        "note_fuzzy_match": "Найдено по неточному совпадению. Пожалуйста, проверьте результат.",
        "followup_text": "Ура! 🎉 Кажется, поиск сработал. Готовы попробовать найти еще один парфюм?",

        "response_not_found_copies": (
            "Не удалось найти подходящих аналогов. Попробуйте ввести полные данные (**Бренд + Название**) или поищите другой аромат. 😣"
        ),
        "response_search_link_prefix": "купить",
        "response_close": "Надеюсь, информация была полезной! ✨",
        "response_note_prefix": "**🤖 Внимание:** ",
        "search_query_buy_word": "купить"
    },
    "en": {
        "button_lang_en": "English 🇬🇧",
        "button_lang_ru": "Русский 🇷🇺",
        "confirm_lang_set": "Language set to English!",
        "go_back": "⬅️ Back",

        "menu_main_text": "👇 **Main Menu**\n\nChoose what you'd like to do:",
        "menu_search": "🔎 Find a Perfume",
        "menu_popular": "🌟 Popular",
        "menu_random": "🎲 Random Scent",
        "menu_history": "📜 My History",

        "search_prompt": "Send me the **Brand + Name** of the fragrance you're looking for.\n\nE.g.: Dior Sauvage.",
        "search_again": "🔎 Search Again",

        "popular_title": "🌟 **Top 10 Popular Fragrances**\n(by number of dupes)",

        "history_title": "📜 **Your History of the last 5 finds**",
        "history_empty": "Your search history is currently empty. Try finding something!",

        "random_title": "🎲 **Random Scent**",
        "random_again": "🎲 Another Random One",

        "welcome": (
            "Hey there! 👋 I can help you find affordable **dupes** for expensive perfumes.\n\n"
            "Please use the menu below to navigate."
        ),
        "error_empty_query": "Oops, I didn't get anything. Please send me the **brand and name of the fragrance**.",
        "error_brand_only": "It looks like you only specified the brand **{brand_name}**. Please specify the perfume name.",
        "error_not_found": "Sorry, I don't know this fragrance yet. 😅 Please check that the brand and name are spelled correctly, or try another one.",
        "note_fuzzy_match": "Found via fuzzy match. Please check the result.",
        "followup_text": "Awesome! 🎉 It seems the search worked. Ready to try finding another perfume?",

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
    lang = lang.lower()
    if lang not in MESSAGES:
        lang = DEFAULT_LANG
    return MESSAGES[lang].get(key, f"<{key} not found for {lang}>")