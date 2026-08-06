import os
import time
import requests
import json
import re

BOT_TOKEN = "8944613696:AAG7iMUW7_oU4O7fEQEISQsl4c4-2L2WR6o"
GROUP_ID = "-1003920918666"

last_update_id = 0
banned = []

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.post(url, json=data)

def get_updates():
    global last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 30}
    r = requests.get(url, params=params)
    return r.json().get("result", [])

print("✅ Бот запущен!")

while True:
    try:
        updates = get_updates()
        for update in updates:
            last_update_id = update["update_id"]

            # === НАЖАТИЕ НА КНОПКУ ===
            if "callback_query" in update:
                query = update["callback_query"]
                data = query["data"]
                chat_id = query["message"]["chat"]["id"]
                user_id = data.split("_")[1]

                if data.startswith("ban_"):
                    if user_id not in banned:
                        banned.append(user_id)
                        send_message(chat_id, f"✅ Пользователь {user_id} заблокирован.")
                    continue

                if data.startswith("unban_"):
                    if user_id in banned:
                        banned.remove(user_id)
                        send_message(chat_id, f"✅ Пользователь {user_id} разблокирован.")
                    continue

                if data.startswith("reply_"):
                    send_message(chat_id, f"✏️ Напиши ответ для клиента {user_id} в эту группу.")
                    continue

            # === СООБЩЕНИЯ ===
            if "message" in update:
                msg = update["message"]
                chat_id = str(msg["chat"]["id"])
                user_id = str(msg["from"]["id"])
                text = msg.get("text", "")
                name = msg["chat"].get("first_name", "Клиент")

                # === ЛИЧКА ===
                if chat_id != GROUP_ID:
                    if user_id in banned:
                        send_message(chat_id, "❌ Вы заблокированы.")
                        continue

                    if text == "/start":
                        send_message(chat_id, f"👋 Привет, {name}!")
                    else:
                        keyboard = {
                            "inline_keyboard": [
                                [
                                    {"text": "✏️ Ответить", "callback_data": f"reply_{user_id}"},
                                    {"text": "🚫 Забанить", "callback_data": f"ban_{user_id}"}
                                ]
                            ]
                        }
                        send_message(GROUP_ID, f"📩 {name} (ID: {user_id}):\n{text}", keyboard)
                        send_message(chat_id, "✅ Отправлено в поддержку!")

                # === ГРУППА ===
                elif chat_id == GROUP_ID:
                    # Если сотрудник пишет ответ на клиента (через кнопку)
                    if text and "reply_" in text:
                        # Ищем ID клиента из последнего сообщения
                        for update2 in updates:
                            if "callback_query" in update2:
                                continue
                        continue

                    # Обычный ответ через "Ответить"
                    if msg.reply_to_message:
                        original = msg.reply_to_message
                        match = re.search(r"ID: (\d+)", original.get("text", ""))
                        if match:
                            client_id = match.group(1)
                            send_message(client_id, f"📨 {text}")
                            send_message(chat_id, "✅ Ответ отправлен!")

        time.sleep(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)