import requests
import time
import json
import re
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8997435855:AAF2AkcieOQ3a_fHGTuVqA2fCPZmnb7-a30")
GROUP_ID = os.getenv("GROUP_ID", "-1003920918666")

# === ПРОКСИ (для обхода блокировок) ===
PROXY = {
    "http": "socks5://45.95.234.102:1080",
    "https": "socks5://45.95.234.102:1080"
}

session = requests.Session()
session.proxies.update(PROXY)
# =====================================

last_update_id = 0
banned = {}

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        session.post(url, json=data, timeout=30)
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def is_admin(chat_id, user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {"chat_id": chat_id, "user_id": user_id}
    try:
        r = session.get(url, params=params, timeout=30)
        if r.status_code == 200:
            status = r.json().get("result", {}).get("status", "")
            return status in ["creator", "administrator"]
    except:
        return False
    return False

def get_updates():
    global last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 30}
    try:
        r = session.get(url, params=params, timeout=30)
        return r.json().get("result", [])
    except:
        return []

print("✅ Бот запущен!")

while True:
    try:
        updates = get_updates()
        for update in updates:
            last_update_id = update["update_id"]

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
                        banned[user_id] = "Без причины"
                        send_message(chat_id, f"✅ {user_id} забанен.")
                    continue

                if data.startswith("unban_"):
                    if user_id in banned:
                        del banned[user_id]
                        send_message(chat_id, f"✅ {user_id} разбанен.")
                    continue

                if data.startswith("reply_"):
                    send_message(chat_id, f"✏️ Напиши ответ для {user_id}:")
                    continue

            if "message" in update:
                msg = update["message"]
                chat_id = str(msg["chat"]["id"])
                user_id = str(msg["from"]["id"])
                text = msg.get("text", "")
                name = msg["chat"].get("first_name", "Клиент")
                username = msg["chat"].get("username", "")

                if chat_id != GROUP_ID:
                    if user_id in banned:
                        reason = banned[user_id]
                        send_message(chat_id, f"❌ Вы заблокированы. Причина: {reason}")
                        continue

                    if text == "/start":
                        send_message(chat_id, f"👋 Привет, {name}!")
                    else:
                        profile_text = f"`{user_id}`\n@{username if username else '—'}\n{text}"
                        keyboard = {
                            "inline_keyboard": [
                                [
                                    {"text": "✏️ Ответить", "callback_data": f"reply_{user_id}"},
                                    {"text": "🚫 Забанить", "callback_data": f"ban_{user_id}"}
                                ]
                            ]
                        }
                        send_message(GROUP_ID, profile_text, keyboard)
                        send_message(chat_id, "✅ Отправлено!")

                elif chat_id == GROUP_ID:
                    if text.startswith("/profile"):
                        if not is_admin(chat_id, user_id):
                            send_message(chat_id, "❌ Только админы могут смотреть профиль.")
                            continue

                        parts = text.split()
                        if len(parts) < 2:
                            send_message(chat_id, "ℹ️ Используй: /profile <ID>")
                            continue

                        target_id = parts[1].strip()
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat"
                        params = {"chat_id": target_id}
                        try:
                            r = session.get(url, params=params, timeout=30)
                            if r.status_code == 200:
                                data = r.json().get("result", {})
                                profile_text = (
                                    f"👤 **Профиль клиента**\n"
                                    f"🆔 ID: `{target_id}`\n"
                                    f"📛 Имя: {data.get('first_name', 'Неизвестно')}\n"
                                    f"📛 Фамилия: {data.get('last_name', '—')}\n"
                                    f"🔖 Username: @{data.get('username', '—')}\n"
                                    f"🚫 Статус: {'❌ Забанен' if target_id in banned else '✅ Активен'}"
                                )
                                if target_id in banned:
                                    profile_text += f"\n📝 Причина бана: {banned[target_id]}"
                                send_message(chat_id, profile_text)
                            else:
                                send_message(chat_id, f"❌ Не найден пользователь с ID: {target_id}")
                        except:
                            send_message(chat_id, f"❌ Не найден пользователь с ID: {target_id}")
                        continue

                    if text.startswith("/ban"):
                        if not is_admin(chat_id, user_id):
                            send_message(chat_id, "❌ Только админы могут банить.")
                            continue

                        parts = text.split(maxsplit=2)
                        if len(parts) < 2:
                            send_message(chat_id, "ℹ️ Используй: /ban <ID> [причина]")
                            continue

                        target_id = parts[1].strip()
                        reason = parts[2] if len(parts) > 2 else "Без причины"

                        if target_id not in banned:
                            banned[target_id] = reason
                            send_message(chat_id, f"✅ {target_id} забанен. Причина: {reason}")
                        else:
                            send_message(chat_id, f"ℹ️ {target_id} уже забанен.")
                        continue

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
                            del banned[target_id]
                            send_message(chat_id, f"✅ {target_id} разблокирован.")
                        else:
                            send_message(chat_id, f"ℹ️ {target_id} не заблокирован.")
                        continue

                    if msg.reply_to_message:
                        original = msg.reply_to_message
                        match = re.search(r"`(\d+)`", original.get("text", ""))
                        if match:
                            client_id = match.group(1)
                            if client_id in banned:
                                keyboard = {
                                    "inline_keyboard": [
                                        [{"text": "🔓 Разблокировать", "callback_data": f"unban_{client_id}"}]
                                    ]
                                }
                                reason = banned[client_id]
                                send_message(chat_id, f"⚠️ Клиент {client_id} забанен. Причина: {reason}", keyboard)
                            else:
                                send_message(client_id, f"📨 {text}")
                                send_message(chat_id, "✅ Ответ отправлен!")

        time.sleep(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
