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

def forward_to_group(bot_token, group_id, msg):
    """Пересылает сообщение (текст, стикер, фото и т.д.) в группу."""
    url = f"https://api.telegram.org/bot{bot_token}/forwardMessage"
    data = {
        "chat_id": group_id,
        "from_chat_id": msg["chat"]["id"],
        "message_id": msg["message_id"]
    }
    requests.post(url, json=data)

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
                user_id = str(msg["from"]["id"])
                user_name = msg["chat"].get("first_name", "Клиент")

                # === ЛИЧКА ===
                if chat_id != GROUP_ID:
                    if user_id in banned_users:
                        send_message(chat_id, "❌ Вы заблокированы за спам.")
                        continue

                    if msg.get("text") and msg["text"] == "/start":
                        send_message(chat_id, f"👋 Привет, {user_name}! Я бот Кальяныч. Напиши свой вопрос.")
                    else:
                        # Пересылаем ВСЁ (текст, стикер, фото, видео) в группу
                        forward_to_group(BOT_TOKEN, GROUP_ID, msg)
                        send_message(chat_id, "✅ Сообщение отправлено в поддержку!")

                # === ГРУППА ===
                elif chat_id == GROUP_ID:
                    text = msg.get("text", "")

                    # Бан
                    if text.lower().startswith("/ban"):
                        if msg.reply_to_message:
                            # ID берём из оригинального сообщения (у него есть from)
                            target_id = str(msg.reply_to_message["from"]["id"])
                            banned_users.add(target_id)
                            send_message(chat_id, f"✅ Пользователь {target_id} заблокирован.")
                        else:
                            send_message(chat_id, "ℹ️ Ответьте на сообщение клиента: /ban")

                    # Разбан
                    elif text.lower().startswith("/unban"):
                        if msg.reply_to_message:
                            target_id = str(msg.reply_to_message["from"]["id"])
                            banned_users.discard(target_id)
                            send_message(chat_id, f"✅ Пользователь {target_id} разблокирован.")
                        else:
                            send_message(chat_id, "ℹ️ Ответьте на сообщение клиента: /unban")

                    # Ответ клиенту (если сотрудник ответил на пересланное сообщение)
                    elif msg.reply_to_message:
                        # Проверяем, что это сообщение от клиента (пересланное в группу)
                        original = msg.reply_to_message
                        if "forward_origin" in original or "forward_from" in original:
                            # Если это пересланное сообщение, берём ID отправителя
                            target_id = str(original["from"]["id"])
                            reply_text = msg.get("text", "")
                            if reply_text:
                                send_message(target_id, f"📨 {reply_text}")
                                send_message(chat_id, "✅ Ответ отправлен!")

        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)