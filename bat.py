import os
import time
import requests
import re

BOT_TOKEN = "8944613696:AAG7iMUW7_oU4O7fEQEISQsl4c4-2L2WR6o"
GROUP_ID = "-1003920918666"

last_update_id = 0
banned = []

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

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
            if "message" in update:
                msg = update["message"]
                chat_id = str(msg["chat"]["id"])
                user_id = str(msg["from"]["id"])
                text = msg.get("text", "")
                name = msg["chat"].get("first_name", "Клиент")

                # === ЛИЧКА ===
                if chat_id != GROUP_ID:
                    if user_id in banned:
                        send_message(chat_id, "❌ Ты забанен.")
                        continue

                    if text == "/start":
                        send_message(chat_id, f"👋 Привет, {name}!")
                    else:
                        send_message(GROUP_ID, f"📩 {name} (ID: {user_id}): {text}")
                        send_message(chat_id, "✅ Отправлено!")

                # === ГРУППА ===
                elif chat_id == GROUP_ID:
                    # БАН
                    if text.startswith("/ban") and msg.reply_to_message:
                        target = str(msg.reply_to_message["from"]["id"])
                        if target not in banned:
                            banned.append(target)
                            send_message(chat_id, f"✅ {target} забанен.")
                        continue

                    # РАЗБАН
                    if text.startswith("/unban") and msg.reply_to_message:
                        target = str(msg.reply_to_message["from"]["id"])
                        if target in banned:
                            banned.remove(target)
                            send_message(chat_id, f"✅ {target} разбанен.")
                        continue

                    # ОТВЕТ КЛИЕНТУ
                    if msg.reply_to_message:
                        original = msg.reply_to_message
                        # Ищем ID в тексте пересланного сообщения
                        match = re.search(r"ID: (\d+)", original.get("text", ""))
                        if match:
                            client_id = match.group(1)
                            send_message(client_id, f"📨 {text}")
                            send_message(chat_id, "✅ Отправлено!")

        time.sleep(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)