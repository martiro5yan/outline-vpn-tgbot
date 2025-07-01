import requests
import sys
import outline

from dotenv import load_dotenv
import os



load_dotenv('config.env')
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

print('удаление ключа')

user_id = sys.argv[1]

message = "Ваш пробный период завершен, ключ удален."

url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

payload = {
    'chat_id': user_id,
    'text': message
}

response = requests.post(url, data=payload)
    # Проверка успешности запроса
if response.status_code == 200:
    print(f"Сообщение {user_id} отправлено!")
    outline.delete_key(user_id)
else:
    print(f"Ошибка: {response.status_code}, {response.text}")
    outline.delete_key(user_id)