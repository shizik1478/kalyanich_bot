import os
import time
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8944613696:AAg7iMUN7_0u40Y7EEO14c4-2L2wR6o"
GROUP_ID = os.environ.get("GROUP_ID") or "-1003920918666"

last_update_id = 0

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def get_updates():
    global last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 30}
    r = requests.get(url, params=params)
    return r.json().get("result", [])

print("🤖 Бот запущен!")

while True:
    try:
        updates = get_updates()
        for update in updates:
            last_update_id = update["update_id"]
            if "message" in update:
                msg = update["message"]
                chat_id = str(msg["chat"]["id"])
                text = msg.get("text", "")
                user_name = msg["chat"].get("first_name", "Клиент")

                if chat_id != GROUP_ID:
                    if text == "/start":
                        send_message(chat_id, f"👋 Привет, {user_name}! Я бот Кальяныч. Напиши свой вопрос.")
                    else:
                        send_message(GROUP_ID, f"📩 {user_name} (ID: {chat_id}):\n{text}")
                        send_message(chat_id, "✅ Сообщение отправлено в поддержку!")
                else:
                    if "reply_to_message" in msg:
                        replied = msg["reply_to_message"]
                        if replied and "text" in replied and "ID:" in replied["text"]:
                            user_id = replied["text"].split("ID: ")[1].split(")")[0]
                            send_message(user_id, f"📨 {msg.get('text', '')}")
                            send_message(GROUP_ID, "✅ Ответ отправлен!")
        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)