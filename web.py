# perfume-bot/web.py
import os
import time
from flask import Flask, request
import telebot
from dotenv import load_dotenv

from database import get_connection, get_copies_by_original_id, log_message, init_db_if_not_exists, fetch_random_original
from search import find_original, _load_catalog
from formatter import format_response, format_popular_list, format_history_list
from i18n import DEFAULT_LANG, get_message
from cache import get_cached_popular_perfumes, get_cached_user_history
import keyboards # <-- Импортируем новый модуль клавиатур

# --- Загрузка окружения и инициализация ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN и WEBHOOK_URL должны быть установлены!")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- Инициализация БД и каталога ---
try:
    conn = get_connection()
    init_db_if_not_exists(conn)
    print("Загрузка каталога в память...")
    _load_catalog(conn)
    print("✅ Каталог успешно загружен.")
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook установлен на URL: {WEBHOOK_URL}")
except Exception as e:
    error_msg = f"FATAL ERROR: Не удалось инициализировать бота: {e}"
    print(error_msg)
    raise

# --- Хранилища в памяти ---
user_language_map = {}
user_states = {} # Простое управление состоянием: {chat_id: "awaiting_search_input"}

# --- ФУНКЦИИ-ХЕНДЛЕРЫ ---

def get_user_lang(chat_id):
    return user_language_map.get(chat_id, DEFAULT_LANG)

@bot.message_handler(commands=['start', 'menu', 'help'])
def send_menu(message):
    chat_id = message.chat.id
    lang = get_user_lang(chat_id)
    user_states.pop(chat_id, None) # Сбрасываем состояние пользователя
    log_message(conn, chat_id, message.text, 'start_command')
    
    welcome_msg = get_message("welcome", lang)
    menu_text = get_message("menu_main_text", lang)
    
    bot.send_message(chat_id, f"{welcome_msg}\n\n{menu_text}", 
                     reply_markup=keyboards.main_menu(lang), 
                     parse_mode='Markdown')

def show_search_prompt(chat_id, lang):
    user_states[chat_id] = "awaiting_search_input"
    prompt_text = get_message("search_prompt", lang)
    bot.send_message(chat_id, prompt_text, 
                     reply_markup=keyboards.back_to_menu(lang),
                     parse_mode='Markdown')

def show_popular(chat_id, lang):
    user_states.pop(chat_id, None)
    popular_perfumes = get_cached_popular_perfumes()
    response = format_popular_list(popular_perfumes, lang)
    bot.send_message(chat_id, response, 
                     reply_markup=keyboards.back_to_menu(lang),
                     parse_mode='Markdown')

def show_history(chat_id, lang):
    user_states.pop(chat_id, None)
    history_items = get_cached_user_history(chat_id)
    response = format_history_list(history_items, lang)
    bot.send_message(chat_id, response, 
                     reply_markup=keyboards.back_to_menu(lang),
                     parse_mode='Markdown')

def show_random(chat_id, lang):
    user_states.pop(chat_id, None)
    original = fetch_random_original(conn)
    if not original:
        # Обработка случая, если база пуста
        bot.send_message(chat_id, "Sorry, I couldn't find any perfume.", reply_markup=keyboards.after_random_menu(lang))
        return

    copies = get_copies_by_original_id(conn, original["id"])
    response_text = format_response(original, copies, lang)
    title = get_message("random_title", lang)
    bot.send_message(chat_id, f"**{title}**\n\n{response_text}",
                     parse_mode='Markdown',
                     disable_web_page_preview=True,
                     reply_markup=keyboards.after_random_menu(lang))


# --- ОБРАБОТЧИКИ НАЖАТИЙ КНОПОК (CALLBACKS) ---

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang:'))
def handle_language_change(call):
    chat_id = call.message.chat.id
    new_lang = call.data.split(':')[1]
    user_language_map[chat_id] = new_lang
    
    confirm_msg = get_message("confirm_lang_set", new_lang)
    bot.answer_callback_query(call.id, text=confirm_msg)
    
    menu_text = get_message("menu_main_text", new_lang)
    bot.edit_message_text(menu_text, chat_id, call.message.message_id,
                          reply_markup=keyboards.main_menu(new_lang),
                          parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('main:'))
def handle_main_menu(call):
    chat_id = call.message.chat.id
    action = call.data.split(':')[1]
    lang = get_user_lang(chat_id)
    bot.answer_callback_query(call.id) # Просто подтверждаем получение

    # Удаляем предыдущее сообщение с кнопками для чистоты интерфейса
    bot.delete_message(chat_id, call.message.message_id)

    if action == 'menu':
        send_menu(call.message)
    elif action == 'search':
        show_search_prompt(chat_id, lang)
    elif action == 'popular':
        show_popular(chat_id, lang)
    elif action == 'history':
        show_history(chat_id, lang)
    elif action == 'random':
        show_random(chat_id, lang)

# --- ГЛАВНЫЙ ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ---

@bot.message_handler(func=lambda msg: True)
def handle_message(msg):
    chat_id = msg.chat.id
    user_text = msg.text.strip()
    lang = get_user_lang(chat_id)

    # Проверяем, ожидает ли бот ввод для поиска
    if user_states.get(chat_id) != "awaiting_search_input":
        send_menu(msg) # Если нет, просто показываем меню
        return

    if not user_text:
        error_msg = get_message("error_empty_query", lang)
        log_message(conn, msg.chat.id, msg.text, 'fail', 'Empty query')
        bot.reply_to(msg, error_msg, parse_mode='Markdown') 
        return

    # --- ЛОГИКА ПОИСКА ---
    result = find_original(conn, user_text, lang=lang) 

    if not result["ok"]:
        log_message(conn, msg.chat.id, msg.text, 'fail', result['message'])
        bot.reply_to(msg, result['message'], parse_mode='Markdown') 
        return

    user_states.pop(chat_id, None) # Сбрасываем состояние после успешного поиска
    original = result["original"]
    copies = get_copies_by_original_id(conn, original["id"])
    
    log_note = f"Found: {original['brand']} {original['name']}"
    if 'note' in result:
        log_note += f" | NOTE: {result['note']}" 
        
    log_message(conn, msg.chat.id, msg.text, 'success', log_note)
    
    response_text = format_response(original, copies, lang=lang)
    
    if 'note' in result:
        note_prefix = get_message("response_note_prefix", lang)
        response_text = f"{note_prefix}{result['note']} \n\n" + response_text 
        
    bot.reply_to(msg, 
                 response_text, 
                 parse_mode='Markdown', 
                 disable_web_page_preview=True,
                 reply_markup=keyboards.after_search_menu(lang)) # <-- Новое меню после поиска


# --- Flask веб-сервер ---
@app.route("/", methods=["GET"])
def index():
    return "Perfume Bot is running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)