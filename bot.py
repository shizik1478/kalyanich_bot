import os
import time
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "8944613696:AAG7iMUW7_oU4O7fEQEISQsl4c4-2L2WR6o"

last_update_id = 0

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text})
        print(f"Ответ на отправку: {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def get_updates():
    global last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 30}
    try:
        r = requests.get(url, params=params)
        print(f"Ответ getUpdates: {r.status_code} {r.text[:100]}")
        return r.json().get("result", [])
    except Exception as e:
        print(f"Ошибка getUpdates: {e}")
        return []

print("🤖 Тестовый бот запущен!")

while True:
    try:
        updates = get_updates()
        for update in updates:
            last_update_id = update["update_id"]
            if "message" in update:
                msg = update["message"]
                chat_id = str(msg["chat"]["id"])
                send_message(chat_id, "✅ Бот отвечает!")
        time.sleep(2)
    except Exception as e:
        print(f"Ошибка в цикле: {e}")
        time.sleep(5)
