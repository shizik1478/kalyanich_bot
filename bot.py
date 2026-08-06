import requests
import time
import json
import os

BOT_TOKEN = "8944613696:AAG7iMUW7_oU4O7fEQEISQsl4c4-2L2WR6o"
GROUP_ID = "-1003920918666"

last_update_id = 0
last_user_id = None

def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps({"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": True})
    requests.post(url, json=data)

def get_updates():
    global last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 30}
    response = requests.get(url, params=params)
    return response.json().get("result", [])

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
                        keyboard = [
                            ["📝 Задать вопрос", "💬 Оставить отзыв"]
                        ]
                        send_message(chat_id, 
                            f"👋 Привет, {user_name}!\n\n"
                            "🔥 Кальяныч на связи!\n"
                            "Напиши свой вопрос или выбери действие.",
                            keyboard
                        )
                        continue
                    
                    if text == "📝 Задать вопрос":
                        send_message(chat_id, "✏️ Напиши свой вопрос, и мы ответим.")
                        continue
                    
                    if text == "💬 Оставить отзыв":
                        send_message(chat_id, "✏️ Напиши свой отзыв или предложение.")
                        continue
                    
                    last_user_id = chat_id
                    send_message(GROUP_ID, f"📩 {user_name} (ID: {chat_id}):\n{text}")
                    send_message(chat_id, "✅ Сообщение отправлено в поддержку!")
                
                elif chat_id == GROUP_ID:
                    if "reply_to_message" in msg:
                        replied = msg["reply_to_message"]
                        if replied and "text" in replied and "ID:" in replied["text"]:
                            user_id = replied["text"].split("ID: ")[1].split(")")[0]
                            reply_text = msg.get("text", "")
                            send_message(user_id, f"📨 {reply_text}")
                            send_message(GROUP_ID, "✅ Ответ отправлен!")
        
        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)