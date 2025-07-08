import telebot
import os
import time
from dotenv import load_dotenv
from datetime import datetime

# Загружаем переменные окружения
load_dotenv('config.env')

TOKEN = os.getenv('TELEGRAM_SUPPORT_TOKEN')
SUPPORT_CHAT_ID = int(os.getenv('SUPPORT_CHAT_ID'))  # Убедитесь, что это int
bot = telebot.TeleBot(TOKEN)

# Словари для хранения данных
pending_requests = {}  # (message_id -> user_id)
user_last_message_time = {}  # (user_id -> timestamp)

def send_night_notice(chat_id):
    """Предупреждение пользователю, если сообщение отправлено ночью (с 00:00 до 06:00)"""
    now = datetime.now()
    if 0 <= now.hour < 8:
        bot.send_message(
            chat_id,
            "❗ Обратите внимание❗\nсейчас ночь, возможно, техподдержка спит. Мы обязательно ответим утром."
        )

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "Привет! Опишите вашу проблему, и мы постараемся помочь."
    )
    send_night_notice(message.chat.id)

@bot.message_handler(content_types=['text', 'photo'], func=lambda message: message.chat.id != SUPPORT_CHAT_ID)
def forward_to_support(message):
    """Пересылает текст или фото пользователя в поддержку с ограничением по времени"""
    user_id = message.from_user.id
    current_time = time.time()
    
    # Ограничение по времени
    if user_id in user_last_message_time:
        last_time = user_last_message_time[user_id]
        if current_time - last_time < 60:
            bot.send_message(message.chat.id, "Вы можете отправлять сообщения не чаще, чем раз в минуту.")
            return

    user_last_message_time[user_id] = current_time

    username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

    # Общая часть сообщения
    header = (
        f"📩 Новая заявка в поддержку\n\n"
        f"👤 Пользователь: {full_name} ({username})\n"
        f"🆔 ID: {user_id}\n\n"
    )

    # Если фото
    if message.photo:
        caption = message.caption if message.caption else "(без подписи)"
        full_caption = header + f"📷 Фото:\n{caption}"

        # Отправляем фото с подписью
        photo = message.photo[-1].file_id  # Самое крупное изображение
        forwarded_message = bot.send_photo(SUPPORT_CHAT_ID, photo=photo, caption=full_caption)
    
    # Если текст
    elif message.text:
        full_text = header + f"💬 Сообщение:\n\n{message.text}"
        forwarded_message = bot.send_message(SUPPORT_CHAT_ID, full_text)

    # Сохраняем ID сообщения
    pending_requests[forwarded_message.message_id] = user_id

    bot.send_message(message.chat.id, "✅ Ваша заявка отправлена в техподдержку.")
    send_night_notice(message.chat.id)

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
