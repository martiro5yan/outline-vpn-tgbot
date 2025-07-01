import sqlite3 as sl
from datetime import datetime, timedelta


db_path = "/home/abragill/db_dir/users.db"

def is_user_in_db(tg_user_id):
    """Проверяет, есть ли пользователь в базе данных по tg_user_id."""
    try:
        con = sl.connect(db_path)
        cur = con.cursor()
        
        cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE tg_user_id = ?)", (tg_user_id,))
        return bool(cur.fetchone()[0])  # Возвращает True, если пользователь есть, иначе False

    except sl.Error:
        return False  # В случае ошибки также возвращаем False

    finally:
        con.close()

def update_purchased_key(tg_user_id, new_key,subscription_period):
    # Подключаемся к базе данных
    con = sl.connect(db_path)
    cur = con.cursor()
    
    try:
        # Получаем текущую дату и время для начала подписки
        subscription_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Рассчитываем дату окончания подписки (например, через 30 дней)
        subscription_end = (datetime.now() + timedelta(days=subscription_period)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Обновляем purchased_key, subscription_start и subscription_end для указанного tg_user_id
        cur.execute("""
            UPDATE users 
            SET purchased_key = ?, subscription_start = ?, subscription_end = ?
            WHERE tg_user_id = ?
        """, (new_key, subscription_start, subscription_end, tg_user_id))
        
        # Сохраняем изменения
        con.commit()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    finally:
        # Закрываем соединение с базой
        con.close()

def add_user_to_trial(tg_user_id):
    """Добавляет пользователя в таблицу trial_users."""
    try:
        # Подключаемся к базе данных
        con = sl.connect(db_path)
        cur = con.cursor()
        
        # Добавляем пользователя в таблицу trial_users
        cur.execute("INSERT INTO trial_users (tg_user_id) VALUES (?)", (tg_user_id,))
        
        con.commit()
        
    except sl.Error as e:
        print(f"Ошибка при добавлении пользователя в базу данных: {e}")
    
    finally:
        # Закрываем соединение с базой данных
        con.close()

def is_user_in_db_trial(tg_user_id):
    """Проверяет, есть ли пользователь в базе данных по tg_user_id."""
    try:
        con = sl.connect(db_path)
        cur = con.cursor()
        
        cur.execute("SELECT EXISTS(SELECT 1 FROM trial_users WHERE tg_user_id = ?)", (tg_user_id,))
        return bool(cur.fetchone()[0])  # Возвращает True, если пользователь есть, иначе False

    except sl.Error:
        return False  # В случае ошибки также возвращаем False

    finally:
        con.close()

def human_readable_date(date_str):
    # Преобразуем строку в объект datetime
    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    # Форматируем в удобочитаемый формат
    human_readable = date_obj.strftime("%d %B %Y, %H:%M:%S")
    
    return human_readable

def get_last_subscription(tg_user_id):
    # Подключаемся к базе данных
    con = sl.connect(db_path)
    cur = con.cursor()
    try:
        # Выполняем запрос, чтобы получить последний день подписки, ключ и tg_user_id
        cur.execute("""
            SELECT tg_user_id, subscription_end, purchased_key 
            FROM USERS 
            WHERE tg_user_id = ? 
            ORDER BY subscription_end DESC LIMIT 1
        """, (tg_user_id,))

        # Получаем результат
        row = cur.fetchone()

        if row:
            tg_user_id, subscription_end, payment_key = row
            return tg_user_id,human_readable_date(subscription_end), payment_key
        
        else:
            return False

    except Exception as e:
        # Обрабатываем ошибки
        print(f"Произошла ошибка: {e}")
    
    finally:
        # Закрываем соединение с базой
        con.close()

def add_db(tg_user_id, first_name, last_name, key,subscription_period):
    # Подключаемся к базе данных
    con = sl.connect(db_path)
    cur = con.cursor()
    
    try:
        # Получаем текущую дату и время для начала подписки
        subscription_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Рассчитываем дату окончания подписки (например, через 30 дней)
        subscription_end = (datetime.now() + timedelta(days=subscription_period)).strftime("%Y-%m-%d %H:%M:%S")

        # Добавляем данные в таблицу
        cur.execute("""
            INSERT INTO USERS (tg_user_id, first_name, last_name, subscription_start, subscription_end, purchased_key)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tg_user_id, first_name, last_name, subscription_start, subscription_end,key))

        # Сохраняем изменения
        con.commit()

        # Выводим все данные из таблицы USERS
        cur.execute("SELECT * FROM USERS")
        rows = cur.fetchall()

    except Exception as e:
        # Если возникает ошибка, выводим ее
        print(f"Произошла ошибка: {e}")
    
    finally:
        # Закрываем соединение с базой
        con.close()


def clear_purchased_key_by_id(tg_user_id):
    """Очищает значение purchased_key у пользователя с tg_user_id."""
    try:
        con = sl.connect(db_path)
        cur = con.cursor()
        
        query = "UPDATE users SET purchased_key = NULL WHERE tg_user_id = ?"
        cur.execute(query, (tg_user_id,))
        
        con.commit()
        con.close()
    except sl.Error as e:
        print(f"Ошибка при обновлении: {e}")



def user_exists(tg_user_id: str) -> bool:
    """Проверяет, есть ли пользователь в базе."""
    con = sl.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT 1 FROM trial_users WHERE tg_user_id = ?", (tg_user_id,))
    result = cur.fetchone()
    con.close()

    return result is not None  # Если запись найдена → True, иначе False

def can_use_discount(tg_user_id: str) -> bool:
    """Проверяет, может ли пользователь воспользоваться скидкой (is_paid = 0)."""
    con = sl.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT is_paid FROM trial_users WHERE tg_user_id = ?", (tg_user_id,))
    result = cur.fetchone()
    con.close()

    return result is not None and result[0] == 0  # Если is_paid = 0 → True, иначе False

def update_trial_status(tg_user_id: str) -> bool:
    """Обновляет статус оплаты (is_paid) с 0 на 1 для пользователя."""
    con = sl.connect(db_path)
    cur = con.cursor()

    # Обновляем значение is_paid с 0 на 1
    cur.execute("""
        UPDATE trial_users
        SET is_paid = 1
        WHERE tg_user_id = ? AND is_paid = 0
    """, (tg_user_id,))

    con.commit()
    con.close()
