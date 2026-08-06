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

def is_admin(chat_id, user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {"chat_id": chat_id, "user_id": user_id}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        status = r.json().get("result", {}).get("status", "")
        return status in ["creator", "administrator"]
    return False

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

            # === КНОПКИ ===
            if "callback_query" in update:
                query = update["callback_query"]
                data = query["data"]
                chat_id = query["message"]["chat"]["id"]
                user_id = data.split("_")[1]
                admin_id = query["from"]["id"]

                if not is_admin(chat_id, admin_id):
                    send_message(chat_id, "❌ Только админы могут это делать.")
                    continue

                if data.startswith("ban_"):
                    if user_id not in banned:
                        banned.append(user_id)
                        send_message(chat_id, f"✅ {user_id} забанен.")
                    continue

                if data.startswith("unban_"):
                    if user_id in banned:
                        banned.remove(user_id)
                        send_message(chat_id, f"✅ {user_id} разбанен.")
                    continue

                if data.startswith("reply_"):
                    send_message(chat_id, f"✏️ Напиши ответ для {user_id}:")
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
                        send_message(chat_id, "✅ Отправлено!")

                # === ГРУППА ===
                elif chat_id == GROUP_ID:
                    # === КОМАНДА /unban <ID> ===
                    if text.startswith("/unban"):
                        if not is_admin(chat_id, user_id):
                            send_message(chat_id, "❌ Только админы могут разблокировать.")
                            continue

                        parts = text.split()
                        if len(parts) < 2:
                            send_message(chat_id, "ℹ️ Используй: /unban <ID>")
                            continue

                        target_id = parts[1].strip()
                        if target_id in banned:
                            banned.remove(target_id)
                            send_message(chat_id, f"✅ Пользователь {target_id} разблокирован.")
                        else:
                            send_message(chat_id, f"ℹ️ Пользователь {target_id} не заблокирован.")
                        continue

                    # Обычный ответ на сообщение
                    if msg.reply_to_message:
                        original = msg.reply_to_message
                        match = re.search(r"ID: (\d+)", original.get("text", ""))
                        if match:
                            client_id = match.group(1)
                            if client_id in banned:
                                keyboard = {
                                    "inline_keyboard": [
                                        [{"text": "🔓 Разблокировать", "callback_data": f"unban_{client_id}"}]
                                    ]
                                }
                                send_message(chat_id, f"⚠️ Клиент {client_id} забанен.", keyboard)
                            else:
                                send_message(client_id, f"📨 {text}")
                                send_message(chat_id, "✅ Ответ отправлен!")

        time.sleep(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)