# CoffeeBot

### Настройка необходимых переменных и директорий
Предварительно необходимо установить [Python 3](https://www.python.org/getit/).
Создайте директорию для проекта и распакуйте в нее файлы из данного репозитория.
Заполните переменные в файле cb_telegram.py:
  - telegram_token - токен_телеграм
  - ms_token - токен для Microsoft Azure Cognitive Services
  - email_smtp_server - SMTP сервер
  - email_login - логин для УЗ почтового сервера
  - email_pwd - пароль для УЗ почтового сервера

Создайте 2 директории для обмена фото:
  - photos
  - sent_images
### Создание окружения и установка библиотек
Для создания окружения и установки необходимых библиотек, перейдите в католог с проектом coffebot и выполните команды
```sh
$ python3 -m venv cb_env
$ source cb_env/bin/activate - для Unix
$ cb_env\Scripts\activate.bat - для Windows
$ pip install python-telegram-bot
$ pip install urllib3
$ python cb_telegram.py
```
### Запуск
Для запуска проекта выполните запуск файла cb_telegram.py
```sh
$ python cb_telegram.py
```
[Инструкция пользователя CoffeeBot](https://github.com/ko90/cofeebot/blob/master/instruction.pdf)
