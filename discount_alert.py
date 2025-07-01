import requests
import text
import sqlite3 as sl
import database
from dotenv import load_dotenv
import os
from datetime import datetime

def list_users():
    con = sl.connect(database.db_path)
    cur = con.cursor()

    cur.execute("SELECT tg_user_id FROM trial_users WHERE is_paid = 0")
    result = cur.fetchall()
    tg_users_id = [user[0] for user in result]
    con.close()
    return tg_users_id  # Возвращаем список пользователей

# Загружаем переменные окружения из файла .env
load_dotenv('config.env')
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
today = datetime.now().date()
# Сообщение, которое нужно отправить
if today.day in [1, 2, 3] and today.month == 5:
    message = text.holiday_text
elif today.day == 9 and today.month == 5:
    message =  text.day_v
else:
    message = text.discount_month

# URL для отправки сообщений через Telegram Bot API
url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

# Получаем список пользователей
tg_users_id = list_users()

# Отправляем сообщение каждому пользователю из списка
for user_id in tg_users_id:
    payload = {
        'chat_id': user_id,
        'text': message
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # выброс исключения при ошибке HTTP
        print(f"Сообщение отправлено пользователю {user_id}!")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка для пользователя {user_id}: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Ошибка соединения для пользователя {user_id}: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Тайм-аут при отправке пользователю {user_id}: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Ошибка запроса для пользователя {user_id}: {req_err}")
    except Exception as e:
        print(f"Непредвиденная ошибка для пользователя {user_id}: {e}")
