# perfume-bot/keyboards.py
from telebot import types
from i18n import get_message

def main_menu(lang: str) -> types.InlineKeyboardMarkup:
    """Генерирует главное меню."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    search = types.InlineKeyboardButton(get_message("menu_search", lang), callback_data="main:search")
    popular = types.InlineKeyboardButton(get_message("menu_popular", lang), callback_data="main:popular")
    random = types.InlineKeyboardButton(get_message("menu_random", lang), callback_data="main:random")
    history = types.InlineKeyboardButton(get_message("menu_history", lang), callback_data="main:history")
    lang_en = types.InlineKeyboardButton(get_message("button_lang_en", lang), callback_data="lang:en")
    lang_ru = types.InlineKeyboardButton(get_message("button_lang_ru", lang), callback_data="lang:ru")
    markup.add(search)
    markup.add(popular, random)
    markup.add(history)
    markup.add(lang_en, lang_ru)
    return markup

def back_to_menu(lang: str) -> types.InlineKeyboardMarkup:
    """Генерирует клавиатуру с кнопкой "Назад в меню"."""
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton(get_message("go_back", lang), callback_data="main:menu")
    markup.add(back_button)
    return markup

def after_search_menu(lang: str) -> types.InlineKeyboardMarkup:
    """Генерирует меню после успешного поиска."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    search_again = types.InlineKeyboardButton(get_message("search_again", lang), callback_data="main:search")
    back_to_main = types.InlineKeyboardButton(get_message("go_back", lang), callback_data="main:menu")
    markup.add(search_again, back_to_main)
    return markup

def after_random_menu(lang: str) -> types.InlineKeyboardMarkup:
    """Гeneрирует меню после показа случайного аромата."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    another_one = types.InlineKeyboardButton(get_message("random_again", lang), callback_data="main:random")
    back_to_main = types.InlineKeyboardButton(get_message("go_back", lang), callback_data="main:menu")
    markup.add(another_one, back_to_main)
    return markup