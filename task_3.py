from bs4 import BeautifulSoup
import urllib.request
import zlib
import brotli
import re
import io
import sqlite3
from flask import Flask, jsonify, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


def get_links():
    links = []
    opener = urllib.request.build_opener()

    opener.addheaders = [('authority', 'mothership.sg'), ('path', '/category/news/'), ('scheme', 'https'),
                         ('accept',
                          'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
                         ('accept-encoding', 'gzip, deflate, sdch, br'), ('accept-language', 'ru,en;q=0.9'),
                         ('cache-control', 'max-age=0'),
                         ('cookie',
                          '__cfduid=d0f27f9a2796d19463bdfb5215521a3fa1594882311; _fbp=fb.1.1594882322449.92315314'),
                         ('if-modified-since', 'Thu, 16 Jul 2020 06:51:31 GMT'), ('referer', 'https://mothership.sg/'),
                         ('sec-fetch-dest', 'document'), ('sec-fetch-mode', 'navigate'),
                         ('sec-fetch-site', 'same-origin'),
                         ('sec-fetch-user', '?1'), ('upgrade-insecure-requests', '1'),
                         ('user-agent',
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 YaBrowser/20.7.0.894 Yowser/2.5 Yptp/1.23 Safari/537.36')]

    fid = opener.open('https://mothership.sg/category/news')
    webpage = fid.read()
    webpage = zlib.decompress(webpage, 16 + zlib.MAX_WBITS).decode("utf-8")
    result = io.StringIO(webpage)

    soup = BeautifulSoup(result, "lxml")
    i = 0;
    for link in soup.body.find_all("a", href=re.compile("https://mothership.sg/\d*/\d*/")):
        l = re.findall(r'<a href=\"(.*)\">', str(link))
        if i < 2 and len(l) > 0:
            links.append(["mothership", l[0]])
            i += 1
        if i >= 2:
            break

    opener.addheaders = [('authority', 'thehardtimes.net'), ('path', '/news/'), ('scheme', 'https'),
                         ('accept',
                          'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
                         ('accept-encoding', 'gzip, deflate, sdch, br'), ('accept-language', 'ru,en;q=0.9'),
                         ('cache-control', 'max-age=0'),
                         ('cookie',
                          '__cfduid=d169fac7ea46934201c28ae0c5a4adcc61594882304; _y=56654d03-4021-482A-0D70-FA9D236D37D5; _shopify_y=56654d03-4021-482A-0D70-FA9D236D37D5; PHPSESSID=vs5jqf82ti0eu67vh9j92pg44f; wordpress_google_apps_login=935060c0747218468e1da9472c41e666; cmplz_choice=set; complianz_policy_id=10; complianz_consent_status=allow; cmplz_id=13220833; _s=578ae6c3-0D0D-4506-A489-B8EBBDC213C7; _shopify_s=578ae6c3-0D0D-4506-A489-B8EBBDC213C7'),
                         ('referer',
                          'https://mstagency.bitrix24.ru/extranet/contacts/personal/user/1352/tasks/task/view/46056/?IFRAME=Y&IFRAME_TYPE=SIDE_SLIDER'),
                         ('sec-fetch-dest', 'document'), ('sec-fetch-mode', 'navigate'),
                         ('sec-fetch-site', 'none'),
                         ('sec-fetch-user', '?1'), ('upgrade-insecure-requests', '1'),
                         ('user-agent',
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 YaBrowser/20.7.0.894 Yowser/2.5 Yptp/1.23 Safari/537.36')]
    fid = opener.open('https://thehardtimes.net/news/')
    webpage = fid.read()
    webpage = brotli.decompress(webpage).decode("utf-8")
    print(webpage)
    result = io.StringIO(webpage)

    soup = BeautifulSoup(result, "lxml")
    i = 0
    for link in soup.body.find_all("a"):
        l = re.findall(r'<a href=\"(https://thehardtimes.net/(?:blog|opinion)/.+)\">', str(link))
        if i < 2 and len(l) > 0:
            if (i > 0 and link_pre != l[0]):
                links.append(["thehardtimes", l[0]])
            elif (i == 0):
                links.append(["thehardtimes", l[0]])
                link_pre = l[0]
            elif (link_pre == l[0]):
                i -= 1
            i += 1
        if i >= 2:
            break

    opener.addheaders = [('authority', 'nypost.com'), ('path', '/news/'), ('scheme', 'https'),
                         ('accept',
                          'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'),
                         ('accept-encoding', 'gzip, deflate, sdch, br'), ('accept-language', 'ru,en;q=0.9'),
                         ('cache-control', 'max-age=0'),
                         ('cookie',
                          'usprivacy=1---; _ncg_id_=bcf2c772-3d2d-4070-9642-d7ae3803134b; _lc2_fpi=37577191df7a--01edb69pkj0syacpgh2d8rhbdm; kw.pv_session=1; _fbp=fb.1.1594882324076.1161600761; OptanonConsent=isIABGlobal=false&datestamp=Thu+Jul+16+2020+16%3A13%3A02+GMT%2B0400+(GMT%2B04%3A00)&version=5.11.0&landingPath=https%3A%2F%2Fnypost.com%2Fnews%2F&groups=C0012%3A1%2CC0013%3A1%2CC0017%3A1&hosts=&consentId=3390f395-4450-4b6f-bb2d-abdb0e48074c&interactionCount=0; _ncg_sp_id.64db=bcf2c772-3d2d-4070-9642-d7ae3803134b.1594882315.1.1594901584.1594882315.ad3c385f-c8ff-449b-ba60-17c6d2ef8c31; _sp_ses.3725=*; _sp_id.3725=b07b26eb6c1642a3.1594882316.4.1594906344.1594901656'),
                         ('referer', 'https://mstagency.bitrix24.ru/extranet/contacts/personal/user/1352/tasks/task/view/46056/?IFRAME=Y&IFRAME_TYPE=SIDE_SLIDER'),
                         ('sec-fetch-dest', 'document'), ('sec-fetch-mode', 'navigate'),
                         ('sec-fetch-site', 'none'),
                         ('sec-fetch-user', '?1'), ('upgrade-insecure-requests', '1'),
                         ('user-agent',
                          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 YaBrowser/20.7.0.894 Yowser/2.5 Yptp/1.23 Safari/537.36')]

    fid = opener.open('https://nypost.com/news/')
    webpage = fid.read()
    webpage = zlib.decompress(webpage, 16 + zlib.MAX_WBITS).decode("utf-8")
    result = io.StringIO(webpage)
    soup = BeautifulSoup(result, "lxml")
    i = 0;
    data = soup.find_all("div", class_="article-loop-container")[0]
    for link in data.find_all("a"):
        l = re.findall(r'<a href=\"(https://nypost.com/\d*/\d*/\d*/.*)\".*>', str(link))
        if i >= 2 and i < 4 and len(l) > 0 and ["nypost", l[0]] not in links:
            links.append(["nypost", l[0]])
            i += 1
        if i < 2:
            i += 1
        if i >= 4:
            break
    return links


# метод для создания подключения к базе данных
def create_connection():
    # конструкция try-except для перехвата ошибок
    try:
        # возвращает объект, который описывает подключение к бд
        return sqlite3.connect('links_database.db')
    except Exception as e:
        print("Ошибка создание связи с бд")
        # вывод ошибки в случае её возникновения
        print(e)
        # проброс ошибки
        raise


# метод создания таблицы, если её не существует в бд
def create_user_table(conn):
    # текст SQL запроса для создания таблицы
    create_users_table = """ CREATE TABLE IF NOT EXISTS links (
                                               id text PRIMARY KEY,
                                               site text NOT NULL,
                                               link text NOT NULL
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


def clear_table(conn):
    # конструкция try-except для перехвата ошибок
    try:
        c = conn.cursor()
        c.execute('DELETE FROM links;', );
        conn.commit()
    except Exception as e:
        print("Ошибка очистки данных таблицы в бд")
        # вывод ошибки в случае её возникновения
        print(e)
        # проброс ошибки
        raise


def insert_data_in_table(id, site, link):
    conn = create_connection()
    c = conn.cursor()
    # текст SQL запроса для создания таблицы
    sql = "INSERT INTO links VALUES (?, ?, ?)"
    # выполнение запроса на добавления информации о новом пользователе в бд
    c.execute(sql, [(id), (site), (link)])
    # отправление изменений в бд
    conn.commit()


def get_data_from_table(site):
    conn = create_connection()
    c = conn.cursor()
    # текст SQL запроса для создания таблицы
    sql = "SELECT link FROM links WHERE site=?"
    # в переменную сохраняем результат выполнения запроса
    res = c.execute(sql, [(site)]).fetchall()
    return res


class Load(Resource):
    def get(self):

        conn = create_connection()
        # создание талбицы
        if conn is not None:
            create_user_table(conn)
            clear_table(conn)
        else:
            print("Error! cannot create the database connection.")
        # сохраняем в переменную объект, который описывает подключение к бд
        # создается повторно, потому что при подключении из другого потока выдает ошибку
        links = get_links()
        i = 0;
        for link in links:
            insert_data_in_table(str(i), link[0], link[1])
            i += 1
        return jsonify({'hello': 'world'})


class Read(Resource):
    def get(self):
        conn = create_connection()
        c = conn.cursor()
        sql = "SELECT * FROM links"
        # в переменную сохраняем результат выполнения запроса
        res = c.execute(sql).fetchall()
        # если в результате есть записи, то такой пользователь уже обращался, иначе добавляем его в бд
        if len(res) > 0:
            arg = request.args.get('')
            if (arg == "mothership"):
                res = get_data_from_table("mothership")
                print(res)
                return jsonify(res)
            elif (arg == "thehardtimes"):
                res = get_data_from_table("thehardtimes")
                print(res)
                return jsonify(res)
            elif (arg == "nypost"):
                res = get_data_from_table("nypost")
                print(res)
                return jsonify(res)
            else:
                return "", 404
        else:
            return "", 403


if __name__ == '__main__':
    # get_links()
    # создание подключения к бд
    api.add_resource(Load, '/load')
    api.add_resource(Read, '/read')
    app.run(debug=True)
