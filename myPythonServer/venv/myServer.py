from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer # импортируем модули для работы с HTTP сервером и запросами
import logging # импортируем модуль для журналирования событий.
import dbEngine # импортируем модуль для работы с БД.
import json


class MyServer(SimpleHTTPRequestHandler):
    """Класс MyServer, наследуется от базового класса - обработчика http запосов BaseHTTPRequestHandler
    содержит методы обработки HTTP запросов
    do_HEAD
    do_GET
    а также вспомогательные методы для взаимодействия с API БД"""

    # Статусы выполнения метода добавления данных.
    STATUS_ADD_DB_OK = 1 # Данные добавились успешно.
    STATUS_ADD_DB_Err = 0 # Добавление данных не удалось.

    def do_HEAD(self):
        # Переопределяем родительский метод do_HEAD. Устанавливает значения для ответа сервера.
        self.send_header("Content-type", "text/html") # Тип контекста (тип данных)
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers() # Добавляем пустую строку, указывающую на конец заголовков HTTP в ответе.

    def do_GET(self):
        # Переопределяем родительский метод do_GET
        """Метод обрабатывает GET запросы, формирует выходной поток для пользователя,
        возвращает json response или None"""
        if self.handler_url() == "get_mysql":
            # обработка события для БД MySQL.
            message = self.get_data_from_MySQL()
            if message is not None:
                self.response_ok('MySQL', 'GET', 'get_all_data', message)
            else:
                self.response_err('MySQL', 'GET', 'get_all_data')
        elif self.handler_url() == "get_redis":
            # обработка события для БД Redis.
            message = self.get_data_from_redis()
            if message is not None:
                self.response_ok('Redis', 'GET', 'get_all_data', message)
            else:
                self.response_err('Redis', 'GET', 'get_all_data')
        elif self.handler_url() == "get_log":
            # обработка события для журнала log.
            self.response_log(self)
        elif self.path == "/":
            self.path = 'template/index.html'
            SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.response_err_in_handler()

    def do_POST(self):
        # Переопределяем родительский метод do_POST
        """Метод обрабатывает POST запросы, формирует выходной поток для пользователя."""
        content_length = int(self.headers.get('content-length', 0)) # Получаем длину тела запроса из headers
                                                                    # исключая пустую строку.
        post_data = str(self.rfile.read(content_length)) # Получаем непосредственно данные их входного потока.
        insert_query = self.get_insert_query(post_data)
        url = self.handler_url()
        if url == "post_mysql":
            # обработка события для БД MySQL.
            if self.add_data_to_MySQL(insert_query):
                self.response_ok('MySQL','POST', 'SAVE', post_data)
            else:
                self.response_err('MySQL','POST', 'SAVE')
        elif url == "post_redis":
            # обработка события для БД Redis.
            if self.add_data_to_redis(insert_query):
                self.response_ok('Redis','POST', 'SAVE', post_data)
            else:
                self.response_err('Redis','POST', 'SAVE')
        else:
            self.response_err_in_handler(self)

    def response_err(self, db_name, method, operation):
        status = 403
        self.send_response(status)
        logging.error(f"Status:{status}: Error in method {method} for {operation} data in {db_name}")
        self.do_HEAD() # Устанавливаем значения в ответ сервера.
        self.wfile.write(f"Server response: Error in operation {operation}".encode('utf-8'))

    def response_ok(self, db_name, method, operation, data=None):
        status = 200
        self.send_response(status)
        logging.info(f"Status:{status}: Method {method} for {operation} user data {data} in {db_name} -- successfully")
        self.do_HEAD() # Устанавливаем значения в ответ сервера.
        self.wfile.write(f"Server response: Operation {operation} successfully".encode('utf-8'))
        for key in data:

            self.wfile.write(f"{key}".encode('utf-8'))

    def response_err_in_handler(self):
        status = 403
        self.send_response(status) # Код ответа 403 - Error.
        logging.error("Error in handler URL not found")
        self.do_HEAD() # Устанавливаем значения в ответ сервера.
        self.wfile.write("Server response: Error in handler URL not found".encode('utf-8'))

    def response_log(self):
        status = 200
        self.send_response(status)
        with open("myserverlogs.json", "r") as file:
            logs = []
            for line in file:
                logs.append(line)
        message = json.dumps(logs)
        self.do_HEAD() # Устанавливаем стандартные значения заголовка в ответ сервера.
        self.wfile.write("Logs : {}".format(message).encode('utf-8'))

    def handler_url(self):
        """Метод обрабатывает url адрес из HTTP,
        возвращает соответствующее строковое обозначение"""
        if self.path == "/save_mysql":
            return "post_mysql"
        if self.path == "/save_redis":
            return "post_redis"
        if self.path == "/get_all_mysql":
            return "get_mysql"
        if self.path == "/get_all_redis":
            return "get_redis"
        if self.path == "/log":
            return "get_log"
        if self.path == '/':
            return "index"

    def get_data_from_MySQL(self):
        """Получает все данные из таблицы БД,
        возвращает ответ пользователю в виде json или None в случае некорректного запроса"""
        dbp = dbEngine.DbParser('config.ini', 'mysql') # создаем объект для парсинга конфигурации                                                                        # для MySQL БД
        pars = dbp.read_db_config() # Получаем конфигурацию из ini файла
        dbe = dbEngine.DbEngineSQL(pars['host'], pars['user'], pars['password'])
        response = dbe.get_all_from_table(pars['database'], pars['table_name']) # получаем даные из БД
        if response is not None:
            response = json.dumps({'record{}'.format(k):v for k, v in enumerate(response)})
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
        """Метод формирует данные для SQL-запроса из данных POST,
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
        if response is not None:
            response = json.dumps(response)
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
