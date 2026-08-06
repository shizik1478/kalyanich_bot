import os
import time
import requests
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "8944613696:AAG7iMUW7_oU4O7fEQEISQsl4c4-2L2WR6o"
GROUP_ID = os.environ.get("GROUP_ID") or "-1003920918666"

last_update_id = 0
banned_users = set()  # Храним ID забаненных

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = keyboard
    requests.post(url, json=data)

def forward_to_group(bot_token, group_id, msg):
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
                text = msg.get("text", "")

                # === ЛИЧКА ===
                if chat_id != GROUP_ID:
                    if user_id in banned_users:
                        send_message(chat_id, "❌ Вы заблокированы за спам.")
                        continue

                    if text == "/start":
                        keyboard = {
                            "keyboard": [
                                ["📝 Задать вопрос", "💬 Оставить отзыв"],
                                ["📦 Статус заказа", "📞 Связаться с менеджером"]
                            ],
                            "resize_keyboard": True,
                            "one_time_keyboard": False
                        }
                        send_message(chat_id, f"👋 Привет, {user_name}!\n\n🔥 Кальяныч на связи!\nВыбери действие:", keyboard)
                    else:
                        forward_to_group(BOT_TOKEN, GROUP_ID, msg)
                        send_message(chat_id, "✅ Сообщение отправлено в поддержку!")

                # === ГРУППА ===
                elif chat_id == GROUP_ID:
                    # Проверяем, есть ли ответ на сообщение
                    if msg.reply_to_message:
                        original = msg.reply_to_message
                        original_text = original.text or ""
                        original_user_id = str(original.from_user.id)

                        # === КОМАНДА /ban ===
                        if text.lower().startswith("/ban"):
                            banned_users.add(original_user_id)
                            send_message(chat_id, f"✅ Пользователь {original_user_id} заблокирован.")
                            continue

                        # === КОМАНДА /unban ===
                        elif text.lower().startswith("/unban"):
                            banned_users.discard(original_user_id)
                            send_message(chat_id, f"✅ Пользователь {original_user_id} разблокирован.")
                            continue

                        # === ОТВЕТ КЛИЕНТУ ===
                        else:
                            # Ищем ID клиента в тексте оригинального сообщения (если это пересланное сообщение)
                            match = re.search(r"ID: (\d+)", original_text)
                            if match:
                                target_id = match.group(1)
                                send_message(target_id, f"📨 {text}")
                                send_message(chat_id, "✅ Ответ отправлен!")
                            else:
                                # Если ID не найден в тексте, пробуем использовать ID отправителя оригинального сообщения
                                send_message(original_user_id, f"📨 {text}")
                                send_message(chat_id, "✅ Ответ отправлен!")
                    else:
                        # Если сотрудник просто пишет в группу без ответа
                        send_message(chat_id, "ℹ️ Нажми 'Ответить' на сообщение клиента, чтобы ответить.")

        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)