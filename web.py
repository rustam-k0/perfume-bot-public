# perfume-bot/web.py
import os
import time
from flask import Flask, request
import telebot
from telebot import types 
from dotenv import load_dotenv

from database import get_connection, get_copies_by_original_id, log_message, init_db_if_not_exists
from search import find_original
from formatter import format_response, welcome_text
from followup import schedule_followup_once
from i18n import DEFAULT_LANG, get_message

# --- Загружаем переменные окружения ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в .env!")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не указан в .env!")

# --- Инициализация бота, базы данных и хранилища языка ---
bot = telebot.TeleBot(BOT_TOKEN)
try:
    conn = get_connection() 
    init_db_if_not_exists(conn)
except Exception as e:
    print(f"FATAL ERROR: Не удалось подключиться к БД: {e}")
    raise

last_user_ts = {}
followup_sent = {}
user_language_map = {} 


# --- Вспомогательная функция для создания кнопок языка ---
def get_language_keyboard(lang=DEFAULT_LANG):
    """Создает Inline-клавиатуру для выбора языка."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"))
    markup.add(types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
    
    start_text = get_message("button_start", lang)
    markup.add(types.InlineKeyboardButton(start_text, callback_data="start_command"))
    return markup


@bot.message_handler(commands=['start'])
def handle_start(msg):
    log_message(conn, msg.chat.id, '/start', 'start_command')
    
    last_user_ts[msg.chat.id] = time.time()
    followup_sent[msg.chat.id] = False
    
    lang = user_language_map.get(msg.chat.id, DEFAULT_LANG)

    bot.send_message(
        msg.chat.id, 
        welcome_text(lang), 
        reply_markup=get_language_keyboard(lang),
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_lang_callback(call):
    chat_id = call.message.chat.id
    new_lang = call.data.split('_')[1]
    
    user_language_map[chat_id] = new_lang
    
    message_text = get_message("language_changed", new_lang).format(lang_code=new_lang.upper())
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=get_language_keyboard(new_lang),
        parse_mode='Markdown'
    )
    bot.answer_callback_query(call.id)
    
@bot.callback_query_handler(func=lambda call: call.data == 'start_command')
def handle_start_callback(call):
    chat_id = call.message.chat.id
    lang = user_language_map.get(chat_id, DEFAULT_LANG)
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=get_message("prompt_search", lang),
        reply_markup=None
    )
    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=['text'])
def handle_text(msg):
    chat_id = msg.chat.id
    now = time.time()
    last_user_ts[chat_id] = now
    followup_sent[chat_id] = False

    lang = user_language_map.get(chat_id, DEFAULT_LANG)
    result = find_original(conn, msg.text, lang=lang)

    if not result['ok']:
        log_message(conn, msg.chat.id, msg.text, 'fail', result['message'])
        bot.reply_to(msg, result['message'], parse_mode='Markdown') 
        return

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
                 disable_web_page_preview=True)

    schedule_followup_once(bot, chat_id, now, last_user_ts, followup_sent, lang=lang)


# --- Flask веб-сервер ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return f"Perfume Bot is running! Default lang: {DEFAULT_LANG}"

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    
    if not bot.get_webhook_info().url:
        bot.set_webhook(url=WEBHOOK_URL)
        
    bot.process_new_updates([update])
    return "ok", 200

# Если запускается локально
if __name__ == '__main__':
    bot.remove_webhook()
    print("Starting bot in polling mode...")
    bot.infinity_polling()