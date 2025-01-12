import sqlite3
import logging
from typing import Tuple

logging.getLogger(__name__)
def sql_start() -> None:
    """"
    Функция для подключения к базе данных
    """
    global base, cur
    base = sqlite3.connect('data_base.db')
    cur = base.cursor()
    if base:
        logging.info('База данных успешно подключена')

    base.execute('''CREATE TABLE IF NOT EXISTS table_request(
                    id PRIMARY KEY,
                    command TEXT NULL,
                    sort_field TEXT DEFAULT 'rating.kp', 
                    sort_type TEXT DEFAULT '1', 
                    limit_request TEXT NULL, 
                    type_number TEXT NULL,
                    search_range TEXT NULL,
                    page TEXT DEFAULT '1')''')

    base.execute('''CREATE TABLE IF NOT EXISTS table_history(
                    id TEXT,
                    command TEXT NULL,
                    sort_field TEXT NULL, 
                    sort_type TEXT NULL, 
                    limit_request TEXT NULL, 
                    type_number TEXT NULL,
                    search_range TEXT NULL,
                    page TEXT NULL)''')

    base.commit()

def add_user(value: str) -> None:
    """
    Функция добавляющая id пользователя в таблицу формирования запроса (table_request)
    """
    cur.execute('INSERT INTO table_request(id) VALUES({value})'.format(value=value))
    base.commit()

def add_info(col: str, value: str, user_id: str) -> None:
    """
    Функция добавляющая значение(value) в таблицу формирования запроса (table_request)
    """
    cur.execute('UPDATE table_request SET {col}={value} WHERE id={user_id}'.format(col=col, value=value, user_id=user_id))
    base.commit()

def result(user_id: str) -> Tuple:
    """
    Функция возвращающая кортеж запроса пользователя по id
    """
    return cur.execute('SELECT * FROM table_request WHERE id={user_id}'.format(user_id=user_id)).fetchone()

def close_base() -> None:
    """
    Функция закрывающая базу данных
    """
    base.close()
    logging.info('База данных закрыта')

def add_request(result: tuple) -> None:
    """
    Функция для записи запроса в таблицу table_history
    """
    cur.execute('INSERT INTO table_history VALUES(?, ?, ?, ?, ?, ?, ?, ?)', result)
    base.commit()

def show_history(user_id: int) -> Tuple:
    """
    Функция возвращающая кортеж из 10 последних запросов пользователя
    """
    return cur.execute('SELECT * FROM (SELECT rowid, * FROM table_history ORDER BY rowid DESC) WHERE id={user_id} LIMIT 10'.format(user_id=user_id)).fetchall()
