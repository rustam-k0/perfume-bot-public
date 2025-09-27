# perfume-bot/followup.py
import time
import threading
from telebot import types
from i18n import get_message

# Время ожидания перед отправкой follow-up сообщения (в секундах)
FOLLOWUP_DELAY = 120

def _send_followup(bot, chat_id, message_text, button_text):
    """Отправляет сообщение с кнопкой повтора."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(button_text, callback_data="start_command"))
    bot.send_message(chat_id, message_text, reply_markup=markup, parse_mode='Markdown')


def schedule_followup_once(bot, chat_id, search_ts, last_user_ts, followup_sent, lang="ru"):
    """
    Запускает таймер для отправки follow-up сообщения,
    если пользователь не взаимодействовал с ботом.
    """
    if followup_sent.get(chat_id):
        return

    def check_and_send():
        """Проверяет условия и отправляет follow-up."""
        # Условие:
        # 1. С момента поиска прошло больше FOLLOWUP_DELAY
        # 2. Последнее действие пользователя было тот самый поиск (search_ts == last_user_ts[chat_id])
        # 3. follow-up еще не отправлен в текущей сессии
        
        if (time.time() - search_ts >= FOLLOWUP_DELAY and
            search_ts == last_user_ts.get(chat_id) and
            not followup_sent.get(chat_id)):
            
            message_text = get_message("followup_message", lang)
            button_text = get_message("followup_button", lang)
            
            _send_followup(bot, chat_id, message_text, button_text)
            followup_sent[chat_id] = True

    # Запускаем проверку в отдельном потоке
    timer = threading.Timer(FOLLOWUP_DELAY, check_and_send)
    timer.start()