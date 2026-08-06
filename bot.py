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
                        send_message(chat_id, f"👋 Привет, {user_name}! Я бот Кальяныч. Напиши свой вопрос.")
                    else:
                        send_message(GROUP_ID, f"📩 {user_name} (ID: {chat_id}):\n{text}")
                        send_message(chat_id, "✅ Сообщение отправлено в поддержку!")
                else:
                    if "reply_to_message" in msg:
                        replied = msg["reply_to_message"]
                        if replied and "text" in replied and "ID:" in replied["text"]:
                            user_id = replied["text"].split("ID: ")[1].split(")")[0]
                            send_message(user_id, f"📨 {msg.get('text', '')}")
                            send_message(GROUP_ID, "✅ Ответ отправлен!")
        time.sleep(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
