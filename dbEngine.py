from getpass import getpass
from mysql.connector import connect, Error
from configparser import ConfigParser
import redis


class DbParser():
    """Вспомогательный класс для работы с БД. Производит парсинг файла конфигурации"""

    def __init__(self, filename='config.ini', section='mysql'):
        self.filename = filename
        self.section = section

    def read_db_config(self):
        """Читает файл конфигурации БД, возвращает словарь параметров для создания ДБ"""
        # создаем парсер и читаем конф ini файл
        parser = ConfigParser()
        parser.read(self.filename)
        # получаем данные из секции [mysql]
        db = {}
        if parser.has_section(self.section):
            items = parser.items(self.section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(section, filename))
        return db


class DbEngineSQL():
    """Класс для взаимодействия с БД MySQL"""
    INSERT_CODE_OK = 1  # операция вставки в БД успешна
    INSERT_CODE_Err = 0  # операция вставки не удалась
    CREATE_DB_CODE_Ok = 1  # операция создания БД успешна
    CREATE_DB_CODE_Err = 0  # операция создания БД не удалась
    CREATE_Table_CODE_Ok = 1  # операция создания таблицы успешна
    CREATE_Table_CODE_Err = 0  # операция создания таблицы не удалась
    ADD_NEW_USER_CODE_Ok = 1  # операция добавление нового пользователя удалась
    ADD_NEW_USER_CODE_Err = 0 # операция добавление нового пользователя не удалась
    CHK_AUTH_USER_Ok = 1  # операция проверки пользователя успешна -- пользователь аутентифицирован
    CHK_AUTH_USER_Err = 0 #   -- пользователь не аутентифицирован

    def __init__(self, host_name, user_name, password, db_name=None):
        self.host_name = host_name
        self.user_name = user_name
        self.password = password
        self.db_name = db_name

    def create_connection(self, db_name):
        """Метод устанавливает соединение с БД MySQL,
        возвращает объект mysql.connector или None в случае неудачи"""
        connection = None
        try:
            if db_name is None:
                connection = connect(
                    host=self.host_name,
                    user=self.user_name,
                    passwd=self.password
                )
            else:
                self.db_name = db_name
                connection = connect(
                    host=self.host_name,
                    user=self.user_name,
                    passwd=self.password,
                    database=self.db_name,
                )
        except Error as e:
            print(f"The error '{e}' for connect DB MySQL")
        return connection

    def create_database(self, db_name):
        """Метод создает БД MySQL,
        возвращает статус операции"""
        query = "CREATE DATABASE" + ' ' + db_name
        connect = self.create_connection()
        cursor = connect.cursor()
        try:
            cursor.execute(query)
            print("Database created successfully")
        except Error as e:
            print(f"The error '{e}' for create DB {db_name} MySQL ")
            return self.CREATE_DB_CODE_Err
        return self.CREATE_DB_CODE_Ok

    def create_table(self, db_name, query):
        """Метод создает таблицу в указаной БД MySQL,
        возвращает статус операции"""
        connect = self.create_connection(db_name)
        try:
            with connect.cursor() as cursor:
                cursor.execute(query)
                connect.commit()
            print(f"Table in '{db_name}' created successfully")
        except Error as e:
            print(f"The error '{e}' for create table MySQL")
            return self.CREATE_Table_CODE_Err
        return self.CREATE_Table_CODE_Ok

    def insert_in_table(self, db_name, table_name, user_data: dict):
        """Метод добавляет в таблицу БД MySQL данные из словаря user_data,
        возвращает статус операции"""
        if len(user_data) != 0 :
            list_values = []
            list_keys = []
            for key, value in user_data.items():
                if value != '':
                    list_values.append(value)
                list_keys.append(key)
            if len(list_values) == len(list_keys):
                user_data['year_of_release'] = int(user_data['year_of_release'])
                keys = ', '.join([str(item) for item in list_keys])
                values = ""
                for item in list_values:
                    if isinstance(item, str):
                        values += f'"{item}"' + ", "
                    else:
                        values += str(item) + ", "
                try:
                    connect = self.create_connection(db_name)
                    query = f"INSERT INTO {table_name} ({keys})" \
                            f" VALUES ({values[0: len(values) - 2]})"
                    with connect.cursor() as cursor:
                        cursor.execute(query)
                        connect.commit()
                    print(f"Table {table_name} in DB {db_name} modify successfully")
                    return self.INSERT_CODE_OK
                except Error as e:
                    print(f"The error '{e}' for insert data in DB MySQL")
        return self.INSERT_CODE_Err

    def add_new_user(self, db_name, user_data: dict):
        del user_data['auth'], user_data['registr']
        if len(user_data) != 0:
            list_values = []
            list_keys = []
            for key, value in user_data.items():
                if value != '':
                    list_values.append(value)
                list_keys.append(key)
            if len(list_values) == len(list_keys):
                values = ""
                for item in list_values:
                    values += f'"{item}"' + ", "
                keys = ', '.join([str(item) for item in list_keys])
                try:
                    connect = self.create_connection(db_name)
                    query = f"INSERT INTO auth_users ({keys})" \
                            f" VALUES ({values[0: len(values) - 2]})"
                    with connect.cursor() as cursor:
                        cursor.execute(query)
                        connect.commit()
                    print(f"Table auth_users in DB {db_name} modify successfully")
                    return self.ADD_NEW_USER_CODE_Ok
                except Error as e:
                    print(f"The error '{e}' for insert new user in DB MySQL")
            return self.ADD_NEW_USER_CODE_Err

    def auth_user(self, db_name, login :str, password:str):
        select_query = f"SELECT * FROM auth_users"
        result = None
        try:
            connect = self.create_connection(db_name)
            with connect.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
            for key in result:
                if key[2] == login and key[3] == password:
                    print(f"user auth successfully")
                    return self.CHK_AUTH_USER_Ok
        except Error as e:
            print(f"The error '{e}' for auth user")
        return self.CHK_AUTH_USER_Err

    def get_all_from_table(self, db_name, table_name):
        """Метод получает из таблицы БД MySQL все данные, для ответа пользоателю,
        возвращает список кортежей или None в случае некорректного запроса"""
        select_query = f"SELECT * FROM {table_name}"
        result = None
        try:
            connect = self.create_connection(db_name)
            with connect.cursor() as cursor:
                cursor.execute(select_query)
                result = cursor.fetchall()
            print(f"Get all data from table MySQL successfully")
        except Error as e:
            print(f"The error '{e}' for get data from BD MySQL")
        return result


class DbEngineRedis():
    """Класс для взаимодействия с БД Redis"""

    INSERT_CODE_OK = 1  # операция вставки в БД успешна
    INSERT_CODE_Err = 0  # операция вставки не удалась

    def __init__(self, hostname, password, port, database_num=0):
        self.hostname = hostname
        self.password = password
        self.port = port
        self.database_num = database_num

    def create_connection(self):
        """Метод устанавливает соединение с БД Redis,
        возвращает объект redis.Redis или None в случае неудачи"""
        connect = None
        try:
            connect = redis.Redis(host=self.hostname, port=self.port, password=self.password, decode_responses=True)
        except Error as e:
            print(f"The error '{e}' to connect Redis")
        return connect

    def insert_in(self, user_data: dict):
        """Метод вставки данных user_data (словарь) в БД Redis,
        возвращает статус выполнения операции"""
        count_empty = 0
        for key, value in user_data.items():
            if value == '':
                count_empty += 1
        if count_empty == 0:
            connect = self.create_connection()
            all_keys = connect.keys('driver*')
            if len(all_keys) != 0:
                all_keys.sort(reverse=True)
            try:
                if len(all_keys) == 0:
                    numder = user_data['id']
                    for key, value in user_data.items():
                        connect.hset(f'driver{numder}', str(key), value)
                else:
                    str_id = all_keys[0]
                    current_id = int(str_id.replace("driver", ''))
                    for key, value in user_data.items():
                        connect.hset(f'driver{str(current_id + 1)}', str(key), value)
                print(f"Record in Ridis modify successfully")
                return self.INSERT_CODE_OK
            except Error as e:
                print(f"The error '{e}' for insert data in Redis")
        return self.INSERT_CODE_Err

    def get_all(self):
        """Метод получает из БД Redis все данные по указанной записи для ответа пользоателю,
        возвращает словарь или None в случае некорректного запроса"""
        result = None
        try:
            connect = self.create_connection()
            all_keys = connect.keys('driver*')
            all_keys.sort()
            result = {}
            for item in all_keys:
                result[item] = connect.hgetall(f'{item}')
            print("Get all data from Ridis record successfully")
        except Error as e:
            print(f"The error '{e}' for get all data from Redis")
        return result