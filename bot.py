import os
import time
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8944613696:AAG7iMUW7_oU4O7fEQEISQsl4c4-2L2WR6o"
GROUP_ID = os.environ.get("GROUP_ID") or "-1003920918666"

last_update_id = 0
banned_users = set()

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
                user_id = str(msg["from"]["id"])

                # Проверка на бан
                if chat_id != GROUP_ID:
                    if user_id in banned_users:
                        send_message(chat_id, "❌ Вы заблокированы за спам.")
                        continue

                if chat_id != GROUP_ID:
                    if text == "/start":
                        send_message(chat_id, f"👋 Привет, {user_name}! Я бот Кальяныч. Напиши свой вопрос.")
                    else:
                        send_message(GROUP_ID, f"📩 {user_name} (ID: {user_id}):\n{text}")
                        send_message(chat_id, "✅ Сообщение отправлено в поддержку!")

                elif chat_id == GROUP_ID:
                    # Обработка команды /ban
                    if text.startswith("/ban"):
                        if msg.reply_to_message:
                            replied = msg.reply_to_message
                            match = replied.text.split("ID: ")
                            if len(match) > 1:
                                user_id = match[1].split(")")[0]
                                banned_users.add(user_id)
                                send_message(chat_id, f"✅ Пользователь {user_id} заблокирован.")
                        else:
                            send_message(chat_id, "ℹ️ Ответьте на сообщение клиента: /ban")

                    # Обработка команды /unban
                    elif text.startswith("/unban"):
                        if msg.reply_to_message:
                            replied = msg.reply_to_message
                            match = replied.text.split("ID: ")
                            if len(match) > 1:
                                user_id = match[1].split(")")[0]
                                banned_users.discard(user_id)
                                send_message(chat_id, f"✅ Пользователь {user_id} разблокирован.")
                        else:
                            send_message(chat_id, "ℹ️ Ответьте на сообщение клиента: /unban")

                    # Обычный ответ сотрудника клиенту
                    elif "reply_to_message" in msg:
                        replied = msg["reply_to_message"]
                        if replied and "text" in replied and "ID:" in replied["text"]:
                            user_id = replied["text"].split("ID: ")[1].split(")")[0]
                            send_message(user_id, f"📨 {msg.get('text', '')}")
                            send_message(GROUP_ID, "✅ Ответ отправлен!")

        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)