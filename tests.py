import requests
import unittest
import dbEngine
class TestPythonHttpServer(unittest.TestCase):

    # Константы состояний ответа
    STATUS_Ok = 1
    STATUS_Err = 0

    headers = {'User-Agent': 'Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'}

    def _do_login(self, login, password):
        sess = requests.Session()
        data = {"auth":1, "registr":0, "login": str(login), "password":str(password)}
        response = sess.get('http://127.0.0.1:8080/')
        self.assertEqual(response.status_code, 200, 'incorrect status code') # проверка статуса страницы login
        response = sess.post('http://127.0.0.1:8080/', data=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, 'incorrect status code') # проверка статуса после аутентификации
        return sess

    def test_login(self, login, password):
        try:
            sess = self._do_login(login, password)
            username = sess.cookies['user_name']
            log = login.replace("@", "%40")
            self.assertEqual(username, log, 'incorrect cookie')
        except Exception:
            return self.STATUS_Err
        return self.STATUS_Ok

    def test_register(self, usename, login, password):
        if not self.test_login(login, password): # если не удалось войти
            try:
                sess1 = requests.Session()
                data = {"auth":0, "registr":1, "user_name":str(usename), "login": str(login), "password":str(password)}
                response = sess1.get('http://127.0.0.1:8080/')
                self.assertEqual(response.status_code, 200, 'incorrect status code')
                response = sess1.post('http://127.0.0.1:8080/', data=data, headers=self.headers) #регистрация в БД
                data = {"auth":1, "registr":0, "login": str(login), "password":str(password)}
                response = sess1.post('http://127.0.0.1:8080/', data=data, headers=self.headers) #запрос на вход
                username = sess1.cookies['user_name']
                log = login.replace("@", "%40")
                self.assertEqual(username, log, 'incorrect cookie')
                return self.STATUS_Ok
            except Exception:
                return self.STATUS_Err
        return self.STATUS_Err

    def test_get_sql(self, login, password):
        try:
            sess = self._do_login(login, password) # сессия с пройденной аутентификацией
            response = sess.get('http://127.0.0.1:8080/get_all_mysql') # запрос данных из MySQL
            self.assertEqual(response.status_code, 200, 'incorrect status code') # проверка статуса ответа
            return self.STATUS_Ok
        except Exception:
            return self.STATUS_Err

    def test_get_redis(self, login, password):
        try:
            sess = self._do_login(login, password) # сессия с пройденной аутентификацией
            response = sess.get('http://127.0.0.1:8080/get_all_redis') # запрос данных из Redis
            self.assertEqual(response.status_code, 200, 'incorrect status code') # проверка статуса ответа
            return self.STATUS_Ok
        except Exception:
            return self.STATUS_Err

    def test_get_log(self, login, password):
        try:
            sess = self._do_login(login, password) # сессия с пройденной аутентификацией
            response = sess.get('http://127.0.0.1:8080/get_log')
            self.assertEqual(response.status_code, 200, 'incorrect status code') # проверка статуса ответа
            return self.STATUS_Ok
        except Exception:
            return self.STATUS_Err

    def test_save_mysql(self, login, password, data):
        dbp = dbEngine.DbParser('config.ini', 'mysql') # создаем объект для парсинга конфигурации sql                                                                       # для MySQL БД
        pars = dbp.read_db_config() # Получаем конфигурацию из ini файла
        dbe = dbEngine.DbEngineSQL(pars['host'], pars['user'], pars['password'])
        try:
            sess = self._do_login(login, password) # сессия с пройденной аутентификацией
            response = sess.post('http://127.0.0.1:8080/save_mysql', data=data, headers=self.headers) # запись в mysql
            self.assertEqual(response.status_code, 200, 'incorrect status code') # проверка статуса ответа
            response = sess.get('http://127.0.0.1:8080/get_all_mysql') # запрос данных из MySQL
            all_data = dbe.get_all_from_table(pars['database'], 'cars')
            values = data.values()
            values = list(values)
            for item in all_data: # проверка совпадения входных данных и данных сохраненных в БД
                index = 0
                count = 0
                for i in range(1, len(item)):
                    if item[i] == values[index]:
                        count += 1
                    if count == len(values):
                        print('OK--')
                        return self.STATUS_Ok
                    elif item[i] != values[index]:
                        break
                    index += 1
        except Exception:
            return self.STATUS_Err
        return self.STATUS_Err


    def test_save_redis(self, login, password, data):
        dbp = dbEngine.DbParser('config.ini', 'redis') # создаем объект для парсинга конфигурации sql                                                                       # для MySQL БД
        pars = dbp.read_db_config() # Получаем конфигурацию из ini файла
        dbe = dbEngine.DbEngineRedis(pars['host'], pars['password'], pars['port'])
        try:
            sess = self._do_login(login, password) # сессия с пройденной аутентификацией
            response = sess.post('http://127.0.0.1:8080/save_redis', data=data, headers=self.headers) # запись в redis
            self.assertEqual(response.status_code, 200, 'incorrect status code') # проверка статуса ответа
            all_data = dbe.get_all()
            values = all_data.values()
            values = list(values)
            for item in values: # проверка совпадения входных данных и данных сохраненных в БД
                if (item['name'] == data['name'] and item['age'] == data['age']
                    and item['exp'] == data['exp'] and item['id'] == data['id']):
                    return self.STATUS_Ok
        except Exception:
            return self.STATUS_Err

test = TestPythonHttpServer()
data_for_sql = {"brand":'nissan', "model":'almera', "year_of_release": 2000, "color":'black'}
data_for_redis = {"id":'21', "name": 'James', "age": '33', "exp": '15'}
login = 'user1@1'
password = '111'

testcase_login = test.test_login(login, password)
#testcase_registr = test.test_register('user78','user78@78', '123456')
testcase_get_sql = test.test_get_sql(login, password)
testcase_get_redis = test.test_get_redis(login, password)
testcase_get_log = test.test_get_log(login, password)
testcase_save_mysql = test.test_save_mysql(login, password, data_for_sql)
testcase_save_redis = test.test_save_redis(login, password, data_for_redis)

print('test login OK') if testcase_login else print('test login Fault')
print('test get MySQL OK') if testcase_get_sql else print('test get MySQL Fault')
print('test get Redis OK') if testcase_get_redis else print('test get Redis Fault')
print('test get Log OK') if testcase_get_log else print('test get Log Fault')
print('test save MySQL OK') if testcase_save_mysql else print('test save MySQL Fault')
print('test save Redis OK') if testcase_save_redis else print('test save Redis Fault')