import re
import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_restful import Resource, Api

file_handler = logging.FileHandler(filename="sample.log")
file_handler.setLevel(logging.ERROR)
logging.root.handlers = [file_handler]

app = Flask(__name__)
api = Api(app)


def get_links_from_mothership():
    """Получает ссылки на две последние новости с сайта mothership.sg"""
    links = []
    url = 'https://mothership.sg/category/news'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    for link in soup.body.find_all("a", href=re.compile("https://mothership.sg/\d*/\d*/")):
        l = re.findall(r'<a href=\"(.*)\">', str(link))
        if len(links) < 2 and len(l) > 0 and ["mothership", l[0]] not in links:
            links.append(["mothership", l[0]])
        else:
            break
    return links


def get_links_from_thehardtimes():
    """Получает ссылки на две последние новости с сайта thehardtimes.net"""
    links = []
    url = 'https://thehardtimes.net/news/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    for link in soup.body.find_all("a"):
        l = re.findall(r'<a href=\"(https://thehardtimes.net/(?:blog|opinion)/.+)\">', str(link))
        if len(links) < 2 and len(l) > 0 and ["thehardtimes", l[0]] not in links:
            links.append(["thehardtimes", l[0]])
        if len(links) >= 2:
            break
    return links


def get_links_from_nypost():
    """Получает ссылки на две последние новости с сайта nypost.com"""
    links = []
    url = 'https://nypost.com/news/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    data = soup.find_all("div", class_="article-loop-container")[0]
    for link in data.find_all("a"):
        l = re.findall(r'<a href=\"(https://nypost.com/\d*/\d*/\d*/.*)\".*>', str(link))
        if len(links) < 2 and len(l) > 0 and ["nypost", l[0]] not in links:
            l = l[0].split('\"')[0]
            links.append(["nypost", l])
        if len(links) >= 2:
            break
    return links


def create_connection():
    """Создаёт объект подключения к базе данных и возвращает его
    В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
      """
    try:
        conn = sqlite3.connect('links_database.db')
        if conn is None:
            raise Exception("Error! Can't create the database connection.")
        return conn
    except Exception as e:
        logging.error(str(e))
        raise



def create_user_table(conn):
    """Создает таблицу в базе данных, если её не существует
    В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
      """
    create_users_table = """ CREATE TABLE IF NOT EXISTS links (
                                               id text PRIMARY KEY,
                                               site text NOT NULL,
                                               link text NOT NULL
                                           ); """
    try:
        c = conn.cursor()
        c.execute(create_users_table)
    except Exception as e:
        logging.error(str(e))
        raise


def clear_table(conn):
    """Очищает все записи в таблице
    В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
      """
    try:
        c = conn.cursor()
        c.execute('DELETE FROM links;', )
        conn.commit()
    except Exception as e:
        logging.error(str(e))
        raise


def insert_data_in_table(id, site, link):
    """Вставляет запись в таблицу
    В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
      """
    try:
        conn = create_connection()
        c = conn.cursor()
        sql = "INSERT INTO links VALUES (?, ?, ?)"
        c.execute(sql, [(id), (site), (link)])
        conn.commit()
    except Exception as e:
        logging.error(str(e))
        raise


def load_links_in_database():
    """Получает ссылки на последние две новости со всех сайтов и вставляет их в базу данных"""
    ID = 0
    for link in get_links_from_mothership():
        insert_data_in_table(str(ID), link[0], link[1])
        ID += 1
    for link in get_links_from_thehardtimes():
        insert_data_in_table(str(ID), link[0], link[1])
        ID += 1
    for link in get_links_from_nypost():
        insert_data_in_table(str(ID), link[0], link[1])
        ID += 1


def get_data_from_table(site):
    """Получает ссылки на послежние новости из бд с указанного сайта"""
    try:
        conn = create_connection()
        c = conn.cursor()
        sql = "SELECT link FROM links WHERE site=?"
        res = c.execute(sql, [(site)]).fetchall()
        return res
    except Exception as e:
        logging.error(str(e))
        raise


class Load(Resource):
    def get(self):
        conn = create_connection()
        clear_table(conn)
        load_links_in_database()
        return jsonify({'hello': 'user'})


class Read(Resource):
    def get(self):
        conn = create_connection()
        c = conn.cursor()
        sql = "SELECT * FROM links"
        res = c.execute(sql).fetchall()
        if len(res) > 0:
            arg = request.args.get('')
            if (arg == "mothership"):
                res = get_data_from_table("mothership")
                return jsonify(res)
            elif (arg == "thehardtimes"):
                res = get_data_from_table("thehardtimes")
                return jsonify(res)
            elif (arg == "nypost"):
                res = get_data_from_table("nypost")
                return jsonify(res)
            else:
                return "", 404
        else:
            return "", 403


if __name__ == '__main__':
    conn = create_connection()
    create_user_table(conn)
    clear_table(conn)
    api.add_resource(Load, '/load')
    api.add_resource(Read, '/read')
    app.run(debug=False)
