import threading
from i18n import get_message

def schedule_followup_once(bot, chat_id, ts, last_user_ts, followup_sent, lang):
    if followup_sent.get(chat_id):
        return

    followup_text = get_message("followup_text", lang)

    def _send():
        if last_user_ts.get(chat_id, 0) == ts and not followup_sent.get(chat_id):
            bot.send_message(chat_id, followup_text)
            followup_sent[chat_id] = True

    t = threading.Timer(30.0, _send)
    t.daemon = True
    t.start()