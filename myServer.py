from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie, Morsel
import logging # импортируем модуль для журналирования событий.
import dbEngine # импортируем модуль для работы с БД.
import json
import datetime, time
import hashlib


class MyServer(SimpleHTTPRequestHandler):
    """Класс MyServer, наследуется от базового класса - обработчика http запосов BaseHTTPRequestHandler
    содержит методы обработки HTTP запросов
    do_HEAD
    do_GET
    а также вспомогательные методы для взаимодействия с API БД"""

    # Статусы выполнения методов.

    STATUS_ADD_DB_OK = 1 # Данные добавились успешно.
    STATUS_ADD_DB_Err = 0 # Добавление данных не удалось.
    STATUS_AUTH_OK = 1 # Аутентификация успешна
    STATUS_AUTH_Err = 0 # Аутентификация не удалась
    STATUS_CHK_COOKIE_Ok = 1 # Cookie содержат ключ доступа
    STATUS_CHK_COOKIE_Err = 0 # Cookie пусты или None
    _auth_users = {} # Словарь текущих аутентифицированных пользователей

    def _check_cookie(self):
        """Внутренний метод класса. Проверяет пользовательский файл cookie
         на наличие ключа доступа. Возвращает статус операции"""
        cookies = SimpleCookie(self.headers.get('Cookie'))
        if len(cookies) != 0:
            if 'auth_key' and 'user_name'in cookies:
                auth_key = cookies['auth_key'].value
                user_name = cookies['user_name'].value
                if auth_key == self._auth_users.get(user_name):
                    return self.STATUS_CHK_COOKIE_Ok
        return self.STATUS_CHK_COOKIE_Err

    def _check_auth(self, insert_query):
        """Внутренний метод класса. Проверяет по условию: существует ли пользователь в БД users,
         или создает нового пользователя в БД users. Возвращает статус операции"""
        dbp = dbEngine.DbParser('config.ini', 'mysql') # создаем объект для парсинга конфигурации                                                                        # для MySQL БД
        pars = dbp.read_db_config() # Получаем конфигурацию из ini файла
        dbe = dbEngine.DbEngineSQL(pars['host'], pars['user'], pars['password'])
        if insert_query['auth'] == '1':
            response = dbe.auth_user(pars['database'], insert_query['login'], insert_query['password']) # получаем даные из БД
            if response:
                return self.STATUS_AUTH_OK
        elif insert_query['registr'] == '1':
            response = dbe.add_new_user(pars['database'], insert_query) # получаем даные из БД
            if response:
                logging.info(f"User {insert_query['login']} created successfull")
                return self.STATUS_AUTH_OK
        return self.STATUS_AUTH_Err

    def _get_hash_key(self, login, password):
        """Внутренний метод класса. Генерирует ключ доступа для пользователя.
        Возвращает ключ в hex формате"""
        current_time = time.localtime()
        time_stamp = time.strftime("%a, %d-%b-%Y %T GMT", current_time)
        input = login + password + time_stamp
        hash_key = hashlib.md5(input.encode())
        return hash_key.hexdigest()

    def _set_cookie(self, auth_key=None, user_name=None):
        """Внутренний метод класса. Устанавливает ключ доступа и username в cookie"""
        self.send_header("Set-Cookie" , f"auth_key={auth_key}")
        self.send_header("Set-Cookie" , f"user_name={user_name}")

    def do_HEAD(self):
        """Метод устанавливает заголовки HTTP в ответ сервера"""
        self.send_header("Content-type", "text/html") # Тип контекста (тип данных)
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers() # Добавляем пустую строку, указывающую на конец заголовков HTTP в ответе.

    def do_GET(self):
        """Метод обрабатывает GET запросы, формирует выходной поток для пользователя,
        возвращает json response или None"""
        if self._check_cookie(): # проверка cookie пользователя на наличие ключа доступа.
            if self.path == "/get_all_mysql":
                # если пользователь имеет ключ доступа - обработка события для БД MySQL.
                message = self.get_data_from_MySQL()
                if message is not None:
                    self.response_ok('MySQL', 'GET', 'get_all_data', message)
                else:
                    self.response_err('MySQL', 'GET', 'get_all_data')
            elif self.path == "/get_all_redis":
                # если пользователь имеет ключ доступа - обработка события для БД Redis.
                message = self.get_data_from_redis()
                if message is not None:
                    self.response_ok('Redis', 'GET', 'get_all_data', message)
                else:
                    self.response_err('Redis', 'GET', 'get_all_data')
            elif self.path == "/get_log":
                # если пользователь имеет ключ доступа - запрос журнала log.
                self.response_log()
            elif self.path == '/':
                # если пользователь имеет ключ доступа открывается страница доступа к БД
                self.path = 'template/index.html'
                SimpleHTTPRequestHandler.do_GET(self)
            elif self.path == '/quit':
                self.send_response(403)
                logging.info(f"User is exit")
                self._set_cookie(auth_key=None, user_name=None)
                self.do_HEAD()
                self.wfile.write(f"Server response: Exit. Please login in again".encode('utf-8'))
        else: # в случае, если cookie пусты или нет ключа доступа, открывается страница аутентификации/регистрации
            self.path = 'template/login.html'
            SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """Метод обрабатывает POST запросы, формирует выходной поток для пользователя."""
        content_length = int(self.headers.get('content-length', 0)) # Получаем длину тела запроса из headers                                                                    # исключая пустую строку.
        post_data = str(self.rfile.read(content_length)) # Получаем непосредственно данные их входного потока.
        insert_query = self.get_insert_query(post_data)
        if self._check_cookie(): # проверка cookie пользователя на наличие ключа доступа.
            if self.path == "/save_mysql":
                # обработка события для БД MySQL.
                if self.add_data_to_MySQL(insert_query):
                    self.response_ok('MySQL','POST', 'SAVE', insert_query)
                else:
                    self.response_err('MySQL','POST', 'SAVE')
            elif self.path == "/save_redis":
                # обработка события для БД Redis.
                if self.add_data_to_redis(insert_query):
                    self.response_ok('Redis','POST', 'SAVE', insert_query)
                else:
                    self.response_err('Redis','POST', 'SAVE')
            else:
                self.response_err_in_handler()
        else: # в случае, если cookie пусты или нет ключа доступа
            if self._check_auth(insert_query): # проверка пользовательских данных
                # если пользователь зарегистрирован, получает ключ дочтупа, и редирект на страницу доступа к БД
                key = self._get_hash_key(insert_query['login'], insert_query['password'])
                self._auth_users[insert_query['login']] = key
                logging.info(f"User {insert_query['login']} login is successfull")
                self.send_response(301)
                self.send_header('Location', '/')
                self._set_cookie(auth_key=key, user_name=insert_query['login']) # устанавливаем key в cookie
                self.do_HEAD()
            else:
                # если пользователь не зарегистрирован, получает сообщение об ошибке доступа
                self.send_response(401) # не авторизован
                self.do_HEAD() # Устанавливаем значения в ответ сервера.
                logging.error(f"Error in login")
                self.wfile.write(f"Server response: Error in login".encode('utf-8'))

    def template_response_html(self):
        """Метод генерирует шаблон HTML для отображения ответа сервера"""
        self.wfile.write(bytes(f"<head><title>MyHTTP-response</title><meta charset='UTF-8'>", "utf-8"))
        self.wfile.write(bytes(f"<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css'>", "utf-8"))
        self.wfile.write(bytes(f"</head>", "utf-8"))
        self.wfile.write(bytes(f"<body><div class='general-container'>", "utf-8"))
        self.wfile.write(bytes(f"<nav class='navbar navbar-expand-sm bg-dark navbar-dark'>", "utf-8"))
        self.wfile.write(bytes(f"<a class='navbar-brand' href='/'>Главная</a>", "utf-8"))
        self.wfile.write(bytes(f"<button class='navbar-toggler' type='button' data-toggle='collapse' data-target='#collapsibleNavbar'>", "utf-8"))
        self.wfile.write(bytes(f"<span class='navbar-toggler-icon'></span>", "utf-8"))
        self.wfile.write(bytes(f"<span class='navbar-toggler-icon'></span>", "utf-8"))
        self.wfile.write(bytes(f"<span class='navbar-toggler-icon'></span>", "utf-8"))
        self.wfile.write(bytes(f"<span class='navbar-toggler-icon'></span>", "utf-8"))
        self.wfile.write(bytes(f"</button></nav></div>", "utf-8"))

    def template_response_data(self, data):
        """Метод подставляет данные ответа в шаблон HTML"""
        self.wfile.write(bytes(f"<p>{data}</p>", "utf-8"))

    def response_err(self, db_name, method, operation):
        """Метод выводит сообщение об ошибке пользователю"""
        status = 400
        self.send_response(status)
        logging.error(f"Status:{status}: Error in method {method} for {operation} data in {db_name}")
        self.do_HEAD() # Устанавливаем значения в ответ сервера.
        self.template_response_html()
        self.wfile.write(f"Server response: Error in operation {operation}".encode('utf-8'))

    def response_ok(self, db_name, method, operation, data):
        """Метод выводит успешный ответ сервера"""
        status = 200
        self.send_response(status)
        logging.info(f"Status:{status}: Method {method} for {operation} user data {data} in {db_name} -- successfully")
        self.do_HEAD() # Устанавливаем значения в ответ сервера.
        self.template_response_html()
        if operation == 'SAVE':
            self.wfile.write(f"Server response: Operation {operation} successfully".encode('utf-8'))
            return
        if operation == 'get_all_data' and db_name == 'Redis':
            for key in data:
                self.wfile.write(bytes(f"<p>{key}: {data[key]}</p>", "utf-8"))

        elif operation == 'get_all_data' and db_name == 'MySQL':
            for item in data:
                self.wfile.write(bytes(f"<p>{item}</p>", "utf-8"))


    def response_err_in_handler(self):
        """Метод выводит сообщение о не корректном адресе в запросе"""
        status = 404
        self.send_response(status)
        logging.error("Error in handler URL not found")
        self.do_HEAD() # Устанавливаем значения в ответ сервера.
        self.template_response_html()
        self.template_response_data(f'Server response {status}: URL not found')

    def response_log(self):
        """Метод выводит логи -- содержимое файла myserverlogs.json,
        возвращает json с логами"""
        status = 200
        self.send_response(status)
        self.do_HEAD()
        logs = []
        self.template_response_html()
        with open("myserverlogs.json", "r") as file:
            for line in file:
                self.template_response_data(line)
                logs.append(line)
        message = json.dumps(logs)
        print('logs OK')
        return message

    def get_data_from_MySQL(self):
        """Получает все данные из таблицы БД,
        возвращает ответ пользователю в виде списка или None в случае некорректного запроса"""
        dbp = dbEngine.DbParser('config.ini', 'mysql') # создаем объект для парсинга конфигурации                                                                        # для MySQL БД
        pars = dbp.read_db_config() # Получаем конфигурацию из ini файла
        dbe = dbEngine.DbEngineSQL(pars['host'], pars['user'], pars['password'])
        response = dbe.get_all_from_table(pars['database'], pars['table_name']) # получаем даные из БД
        return response

    def add_data_to_MySQL(self, insert_query):
        """Записываем данные в таблицу БД MySQL,
        возвращает статус выполнения операции"""
        dbp = dbEngine.DbParser('config.ini', 'mysql') # создаем объект для парсинга конфигурации sql                                                                       # для MySQL БД
        pars = dbp.read_db_config() # Получаем конфигурацию из ini файла
        dbe = dbEngine.DbEngineSQL(pars['host'], pars['user'], pars['password'])
        if (dbe.insert_in_table(pars['database'], pars['table_name'], insert_query)):
            return self.STATUS_ADD_DB_OK
        return self.STATUS_ADD_DB_Err

    def get_insert_query(self, post_data):
        """Метод формирует данные для запроса из данных POST,
        возвращает словарь - данные для SQL запроса"""
        isert_query = {}
        post_data = post_data.replace(' ', '')
        if len(post_data) > 3:
            message = post_data.replace('"', '').replace('=', ':')
            list_message = message[2:len(message)-1].split('&')
            for item in list_message:
                list_item = item.split(':')
                isert_query[list_item[0]] = list_item[1]
        return isert_query

    def get_data_from_redis(self):
        """Метод получает данные из API БД ,
        возвращает ответ пользователю в json или None в случае неудачного запроса"""
        dbp = dbEngine.DbParser('config.ini', 'redis') # создаем объект для парсинга конфигурации redis
        pars = dbp.read_db_config()
        dbe = dbEngine.DbEngineRedis(pars['host'], pars['password'], pars['port']) # создаем объект API БД
        response = dbe.get_all()
        return response

    def add_data_to_redis(self, post_data):
        """Метод, используя API БД, добавляет данные в Redis,
        возвращает статус операции"""
        dbp = dbEngine.DbParser('config.ini', 'redis') # создаем объект для парсинга конфигурации redis
        pars = dbp.read_db_config()
        dbe = dbEngine.DbEngineRedis(pars['host'], pars['password'], pars['port']) # создаем объект API БД
        if dbe.insert_in(post_data):
            return self.STATUS_ADD_DB_OK
        return self.STATUS_ADD_DB_Err

def run(server_class=HTTPServer, handler_class=MyServer, port=8080):
    # Функция для инициализации и запуска нашего сервера.
    logging.basicConfig(filename='myserverlogs.json', level=logging.INFO) # Устанавливаем уровень логирования - логирование в консоль и в журнал.
    server_address = ("127.0.0.1", port)
    httpd = server_class(server_address, handler_class) # Создаем эеземпляр класса HTTPServer. Он создает и
                                                        # слушает HTTP-сокет, отправляя запросы обработчику.
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever() # Режим обработки: по одному запросу безконечно долго.
    except Exception:
        print('^C received, shutting down server')
        httpd.shutdown()
        print('server is shutting down')
    httpd.server_close()
    logging.info('Stopping httpd...\n')

run()