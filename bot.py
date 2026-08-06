import os
import time
import requests
import re
import json

BOT_TOKEN = "8944613696:AAG7iMUW7_oU4O7fEQEISQsl4c4-2L2WR6o"
GROUP_ID = "-1003920918666"

last_update_id = 0
banned = []
waiting_for_reply = {}

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.post(url, json=data)

def send_to_group(msg, user_id, name, text):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✏️ Ответить", "callback_data": f"reply_{user_id}"},
                {"text": "🚫 Забанить", "callback_data": f"ban_{user_id}"}
            ]
        ]
    }
    send_message(GROUP_ID, f"📩 {name} (ID: {user_id}):\n{text}", keyboard)

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

            # === ОБРАБОТКА КНОПОК ===
            if "callback_query" in update:
                query = update["callback_query"]
                data = query["data"]
                chat_id = query["message"]["chat"]["id"]
                user_id = data.split("_")[1]

                if data.startswith("ban_"):
                    if user_id not in banned:
                        banned.append(user_id)
                        send_message(chat_id, f"✅ Пользователь {user_id} заблокирован.")
                    else:
                        send_message(chat_id, f"ℹ️ Пользователь {user_id} уже заблокирован.")
                    continue

                if data.startswith("reply_"):
                    waiting_for_reply[chat_id] = user_id
                    send_message(chat_id, f"✏️ Напиши ответ для клиента {user_id}:")
                    continue

            # === ОБРАБОТКА СООБЩЕНИЙ ===
            if "message" in update:
                msg = update["message"]
                chat_id = str(msg["chat"]["id"])
                user_id = str(msg["from"]["id"])
                text = msg.get("text", "")
                name = msg["chat"].get("first_name", "Клиент")

                # === ЛИЧКА ===
                if chat_id != GROUP_ID:
                    if user_id in banned:
                        send_message(chat_id, "❌ Вы заблокированы за спам.")
                        continue

                    if text == "/start":
                        send_message(chat_id, f"👋 Привет, {name}!\nНапиши свой вопрос.")
                    else:
                        send_to_group(msg, user_id, name, text)
                        send_message(chat_id, "✅ Сообщение отправлено в поддержку!")

                # === ГРУППА ===
                elif chat_id == GROUP_ID:
                    # === КОМАНДА /unban ===
                    if text.lower().startswith("/unban"):
                        if msg.reply_to_message:
                            original = msg.reply_to_message
                            match = re.search(r"ID: (\d+)", original.get("text", ""))
                            if match:
                                client_id = match.group(1)
                                if client_id in banned:
                                    banned.remove(client_id)
                                    send_message(chat_id, f"✅ Пользователь {client_id} разблокирован.")
                                else:
                                    send_message(chat_id, f"ℹ️ Пользователь {client_id} не заблокирован.")
                            else:
                                send_message(chat_id, "❌ Не найден ID в сообщении.")
                        else:
                            send_message(chat_id, "ℹ️ Ответьте на сообщение клиента: /unban")
                        continue

                    # === ОТВЕТ НА СООБЩЕНИЕ ===
                    if chat_id in waiting_for_reply:
                        client_id = waiting_for_reply[chat_id]
                        if text.strip():
                            send_message(client_id, f"📨 {text}")
                            send_message(chat_id, f"✅ Ответ отправлен клиенту {client_id}.")
                            del waiting_for_reply[chat_id]
                        continue

                    if msg.reply_to_message:
                        original = msg.reply_to_message
                        match = re.search(r"ID: (\d+)", original.get("text", ""))
                        if match:
                            client_id = match.group(1)
                            send_message(client_id, f"📨 {text}")
                            send_message(chat_id, "✅ Ответ отправлен!")

        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)