import telebot
import os
import time
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('config.env')

TOKEN = os.getenv('TELEGRAM_SUPPORT_TOKEN')
SUPPORT_CHAT_ID = int(os.getenv('SUPPORT_CHAT_ID'))  # Убедитесь, что это int
bot = telebot.TeleBot(TOKEN)

# Словари для хранения данных
pending_requests = {}  # (message_id -> user_id)
user_last_message_time = {}  # (user_id -> timestamp)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Опишите вашу проблему, и мы постараемся помочь.")

@bot.message_handler(func=lambda message: message.chat.id != SUPPORT_CHAT_ID)
def forward_to_support(message):
    """Пересылает сообщение пользователя в поддержку с ограничением по времени"""
    user_id = message.from_user.id
    current_time = time.time()
    
    # Проверяем, когда пользователь отправлял последнее сообщение
    if user_id in user_last_message_time:
        last_time = user_last_message_time[user_id]
        if current_time - last_time < 60:  # 60 секунд = 1 минута
            bot.send_message(message.chat.id, "Вы можете отправлять сообщения не чаще, чем раз в минуту.")
            return

    # Обновляем время последнего сообщения
    user_last_message_time[user_id] = current_time

    username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

    # Формируем текст заявки с эмодзи
    formatted_text = (
        f"📩 Новая заявка в поддержку\n\n"
        f"👤 Пользователь: {full_name} ({username})\n"
        f"🆔 ID: {user_id}\n\n"
        f"💬 Сообщение:\n\n{message.text}"
    )

    # Отправляем сообщение в поддержку
    forwarded_message = bot.send_message(SUPPORT_CHAT_ID, formatted_text)

    # Сохраняем связь message_id -> user_id
    pending_requests[forwarded_message.message_id] = user_id

    bot.send_message(message.chat.id, "✅ Ваша заявка отправлена в техподдержку.")

@bot.message_handler(func=lambda message: message.chat.id == SUPPORT_CHAT_ID and message.reply_to_message)
def reply_to_user(message):
    """Позволяет техподдержке отвечать пользователю"""
    support_msg_id = message.reply_to_message.message_id
    user_id = pending_requests.get(support_msg_id)

    if user_id:
        bot.send_message(user_id, f"📩 Ответ от техподдержки:\n\n{message.text}")
        bot.send_message(message.chat.id, "✅ Ответ отправлен пользователю.")
    else:
        bot.send_message(message.chat.id, "⚠ Ошибка: Исходное сообщение не найдено.")

bot.polling(none_stop=True)
