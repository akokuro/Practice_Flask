# подключение класса request из модуля flask
from flask import request
# подключение класса Flask из модуля flask
from flask import Flask
# подключение модуля sqlite3 для работы с бд
import sqlite3
# подключение модуля datetime для работы с датой и временем
import datetime

# создаётся объект класса Flask
app = Flask(__name__)


# метод для создания подключения к базе данных
def create_connection():
    # конструкция try-except для перехвата ошибок
    try:
        # возвращает объект, который описывает подключение к бд
        return sqlite3.connect('test_database.db')
    except Exception as e:
        print("Ошибка создание связи с бд")
        # вывод ошибки в случае её возникновения
        print(e)
        # проброс ошибки
        raise


# метод создания таблицы, если её не существует в бд
def create_user_table(conn):
    # текст SQL запроса для создания таблицы
    create_users_table = """ CREATE TABLE IF NOT EXISTS user (
                                               id text PRIMARY KEY,
                                               date_connect text NOT NULL
                                           ); """
    # конструкция try-except для перехвата ошибок
    try:
        # в переменную c сохраняем специальный объект, который делает запросы и получает их результаты
        c = conn.cursor()
        # выполняем запрос create_users_table
        c.execute(create_users_table)
    except Exception as e:
        print("Ошибка создание таблицы в бд")
        # вывод ошибки в случае её возникновения
        print(e)
        # проброс ошибки
        raise


# вызывается метод route объекта app, в который передается адрес страницы и методы, возвращается функция декоратор
# в функцию декоратор передается ссылка на функцию see
# функция декоратор регестрирует функцию see как обработчик запросов по указанному адресу
@app.route('/see', methods=['POST'])
def see():
    # сохраняем в переменную объект, который описывает подключение к бд
    # создается повторно, потому что при подключении из другого потока выдает ошибку
    conn = create_connection()
    # конструкция try-except для перехвата ошибок
    try:
        # в переменную c сохраняем специальный объект, который делает запросы и получает их результаты
        c = conn.cursor()
        # текст SQL запроса для создания таблицы
        sql = "SELECT * FROM user WHERE id=?"
        # в переменную сохраняем результат выполнения запроса
        res = c.execute(sql, [(request.remote_addr)]).fetchall()
        # если в результате есть записи, то такой пользователь уже обращался, иначе добавляем его в бд
        if len(res) > 0:
            # текст SQL запроса для создания таблицы
            sql = "UPDATE user SET date_connect =? WHERE id =?"
            # выполнение запроса на обновление информации о последнем образении пользователя
            c.execute(sql, [(datetime.datetime.now()), (request.remote_addr)])
            # отправление изменений в бд
            conn.commit()
            # возврат пользователю привета и времени последнего обращения
            return "Hello " + res[0][1]
        else:
            # текст SQL запроса для создания таблицы
            sql = "INSERT INTO user VALUES (?, ?)"
            # выполнение запроса на добавления информации о новом пользователе в бд
            c.execute(sql, [(request.remote_addr), (datetime.datetime.now())])
            # отправление изменений в бд
            conn.commit()
            # возврат ошибки 204
            return '', 204
    except Exception as e:
        # вывод ошибки в случае её возникновения
        print(e)
        # проброс ошибки
        raise


if __name__ == '__main__':
    # создание подключения к бд
    conn = create_connection()
    # создание талбицы
    if conn is not None:
        create_user_table(conn)
    else:
        print("Error! cannot create the database connection.")
    # вызывызавется метода run объекта app: запуск приложения в режиме debug
    app.run(debug=True)
# "ресурс" в жаргоне http - это, по сути, всё, что загружает браузер (изображения, файлы JavaScript, CSS и прочее)
# Статус-код 200 говорит о том, что запрос успешно выполнен,
# а статус-код 204 о том, что запрос выполнен успешно, но  в ответе были переданы только заголовки без тела сообщения
