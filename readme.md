HTTP Server Python
===

---

Структура проекта:

- конфиг файлы в которых содержится вся необходимая для функционирования
 проекта информация (в том числе для бд, в отдельном файле)
- requirements.txt - файл в котором содержится список установленных модулей
- .py файлы проекта


---
Описание:  

HTTP с простым UI с возможностью элементарной аутентификации/регистрации, принимает post/get запросы.

Типы post запросов:
1) Запрос на сохранение данных в SQL бд (MYSQL 8.0)
2) Запрос на сохранение данных в redis
При всех запросах сохраняемые данные и полученные статусы request/response  
дублируются в log.json

Типы get запросов:
1) Запрос на получение всех данных из redis
2) Запрос на получение всех данных из mysql
3) Запрос на получение всех данных из log.json


Сервер реализован без использования сторонних фреймворков и ORM

