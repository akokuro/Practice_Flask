import re
import logging
import sqlite3
import requests
from functools import reduce
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_restful import Resource, Api

file_handler = logging.FileHandler(filename="sample.log")
file_handler.setLevel(logging.ERROR)
logging.root.handlers = [file_handler]

app = Flask(__name__)
api = Api(app)


class Parser():
    sites = {"mothership": "https://mothership.sg/category/news",
             "thehardtimes": "https://thehardtimes.net/news/",
             "nypost": "https://nypost.com/news/"}
    sites_pattern = {"mothership": re.compile(r"https://mothership.sg/\d*/\d*/"),
                     "thehardtimes": re.compile(r"https://thehardtimes.net/(?:blog|opinion)/.+"),
                     "nypost": re.compile(r"https://nypost.com/\d*/\d*/\d*/.*")}

    def __init__(self, source: str):
        self.source = source

    def get_links(self):
        url = Parser.sites.get(self.source)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")
        pattern = Parser.sites_pattern.get(self.source)
        all_links = [link for link in soup.body.find_all("a", href=pattern)]
        result = reduce(lambda initializer, element:
                        initializer.append([self.source, element['href']]) or
                        initializer if element not in initializer else initializer,
                        all_links, [])[:2]
        return result


class NewsDatabase:
    def __init__(self):
        self.conn = self.create_connection()
        self.create_links_table()

    def create_connection(self):
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

    def create_links_table(self):
        """Создает таблицу в базе данных, если её не существует
        В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
          """
        create_users_table = """ CREATE TABLE IF NOT EXISTS links (
                                                   id text PRIMARY KEY,
                                                   site text NOT NULL,
                                                   link text NOT NULL
                                               ); """
        try:
            c = self.conn.cursor()
            c.execute(create_users_table)
        except Exception as e:
            logging.error(str(e))
            raise

    def clear_table(self):
        """Очищает все записи в таблице
        В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
          """
        try:
            c = self.conn.cursor()
            c.execute('DELETE FROM links;', )
            self.conn.commit()
        except Exception as e:
            logging.error(str(e))
            raise

    def insert_data_in_table(self, id, site, link):
        """Вставляет запись в таблицу
        В случае ошибки, записывает информацию о ней в лог-файл и пробрасывает ошибку дальше
          """
        try:
            c = self.conn.cursor()
            sql = "INSERT INTO links VALUES (?, ?, ?)"
            c.execute(sql, [(id), (site), (link)])
            self.conn.commit()
        except Exception as e:
            logging.error(str(e))
            raise

    def load_links_in_database(self):
        """Получает ссылки на последние две новости со всех сайтов и вставляет их в базу данных"""
        ID = 0
        for link in Parser("mothership").get_links():
            self.insert_data_in_table(str(ID), link[0], link[1])
            ID += 1
        for link in Parser("thehardtimes").get_links():
            self.insert_data_in_table(str(ID), link[0], link[1])
            ID += 1
        for link in Parser("nypost").get_links():
            self.insert_data_in_table(str(ID), link[0], link[1])
            ID += 1

    def get_data_from_table(self, site):
        """Получает ссылки на послежние новости из бд с указанного сайта"""
        try:
            c = self.conn.cursor()
            sql = "SELECT link FROM links WHERE site=?"
            res = c.execute(sql, [(site)]).fetchall()
            return res
        except Exception as e:
            logging.error(str(e))
            raise


class Load(Resource):

    def get(self):
        newsDB = NewsDatabase()
        newsDB.clear_table()
        newsDB.load_links_in_database()
        return jsonify({'hello': 'user'})


class Read(Resource):
    def get(self):
        newsDB = NewsDatabase()
        arg = request.args.get('')
        if arg not in Parser.sites.keys():
            return "", 404
        res = newsDB.get_data_from_table(arg)
        if len(res) > 0:
            return jsonify(res)
        else:
            return "", 403


if __name__ == '__main__':
    newsDB = NewsDatabase()
    newsDB.clear_table()
    api.add_resource(Load, '/load')
    api.add_resource(Read, '/read')
    app.run(debug=False)
