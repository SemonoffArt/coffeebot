import telebot
import sqlite3
import random
import sched, time
from re import *
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from math import radians, cos, sin, asin, sqrt
import threading
from threading import Thread, Event
from timeit import Timer
import datetime
from cb_azure import *
from cb_db_functions import *
from cb_email import *
from cb_locations import *


telegram_token = "" #токен_телеграм
ms_token = "" #токен для microsoft azure cs
email_smtp_server = "" #SMTP сервер
email_login = "" #логин для УЗ почтового сервера
email_pwd = "" #пароль для УЗ почтового сервера


bot = telebot.TeleBot(telegram_token)
file_db = "cb.db"
conn = sqlite3.connect(file_db)
cursor = conn.cursor()
name = ''
surname = ''
email = ''
code = ''
location_id = ""


class cbClass():
    global bot
    global ms_token
    global email_smtp_server
    global email_login
    global email_pwd
    def __init__(self):
        pass

    def cbFunc(self):
        file_db = "cb.db"
        conn = sqlite3.connect(file_db)
        cursor = conn.cursor()
        global name
        global surname
        global email
        global location_id

        #Определние дистанции
        def distance(lat1, lon1, lat2, lon2):
            """
            Calculate the great circle distance between two points
            on the earth (specified in decimal degrees)
            """
            # convert decimal degrees to radians
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            # haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            km = 6367 * c
            return km

        #Определение ближайшей локации
        def nearestLocation(lon,lat):
            conn = sqlite3.connect(file_db)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM locations')
            data = cursor.fetchall()
            nl = {}
            for location in data:
                dist = distance(float(lon), float(lat), float(location[4]), float(location[3]))
                if nl == {}:
                    nl = {
                        'location_id': location[0],
                        'location_town': location[1],
                        'location_address': location[2],
                        'distance': dist
                    }
                elif nl['distance'] > dist:
                    nl = {
                        'location_id': location[0],
                        'location_town': location[1],
                        'location_address': location[2],
                        'distance': dist
                    }
            return nl

        #Функции для диалога с пользователем
        @bot.message_handler(content_types=['text'])
        def start(message):
            if checkUser(file_db, message.from_user.id):
                if checkUserInQueue(file_db, message.from_user.id):
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 2
                    markup.add(InlineKeyboardButton("Я уже не хочу кофе", callback_data="cancel_queue"))
                    bot.send_message(message.from_user.id, checkUser(file_db, message.from_user.id) + ", я помню, что ты хочешь пойти попить кофейку. Как только я найду для тебя пару, сразу сообщу.", reply_markup=markup)

                elif message.text == '/stopchat':
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 2
                    markup.add(InlineKeyboardButton("Да", callback_data="stopchat_yes"),
                                               InlineKeyboardButton("Нет", callback_data="stopchat_no"))
                    bot.send_message(message.from_user.id, "Вы желаете остановить диалог с собеседником?", reply_markup=markup)

                elif message.text == '/showcs':
                    InfoByTelegramId = getInfoByTelegramId(file_db, message.from_user.id)
                    location_id = InfoByTelegramId['location_id']
                    location_info = getLocationInfo(file_db, location_id)
                    #Делаем 5 попыток получить ближайшие места, потому что бывает что сервис Google отвечает пустым ответом
                    i = 5
                    while i > 0:
                        nearest_coffee = getLocations(location_info[3],location_info[4],"AIzaSyBFE4VdqZXTAYEfRRiUIRLss12UBsTfh2U", 10)
                        if nearest_coffee != "":
                            i = 0
                        else:
                            i = i - 1
                    if nearest_coffee != "":
                        bot.send_message(message.from_user.id, "Ближайшие места, где можно попить кофе:\n" + nearest_coffee, parse_mode="Markdown", disable_web_page_preview=True)

                    else:
                        bot.send_message(message.from_user.id, "К сожалению, не удалось ничего найти. Иногда нас подводит сервис Google, попробуй повторить /showcs")

                elif checkActiveDialog(file_db, message.from_user.id):
                    #bot.send_message(message.from_user.id, "У тебя есть активный диалог")
                    text = str("Вам пишет {0}: ".format(checkUser(file_db, message.from_user.id)))
                    bot.send_message(getCompanionId(file_db, message.from_user.id), text + message.text)

                else:
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 2
                    markup.add(InlineKeyboardButton("Да", callback_data="cb_yes"),
                                               InlineKeyboardButton("Пока не готов", callback_data="cb_no"))
                    bot.send_message(message.from_user.id, "Привет, " + checkUser(file_db, message.from_user.id) + "! Пора попить кофейку ☕️ ?", reply_markup=markup)

            elif getCode(file_db, message.from_user.id):
                infoCode = getCode(file_db, message.from_user.id)
                bot.send_message(message.from_user.id, 'На твою почту ' + infoCode[3] + ' был отправлен код подтверждения. Пожалуйста, введи его. Если ты ошибся при вводе e-mail, нажми /setemail')
                bot.register_next_step_handler(message, get_check_pin)
            else:
                if message.text == '/reg':
                    bot.send_message(message.from_user.id, "Регистрация займет пару минут! Чтобы мне удостовериться, что ты из банка Открытие, потребуется подтверждение по E-mail. Введи адрес своей корпоративной почты email@open.ru")
                    bot.register_next_step_handler(message, get_email); #следующий шаг – функция get_email
                else:
                    bot.send_message(message.from_user.id, 'Добро пожаловать в CoffeeBot! Этот чатбот поможет найти собеседника на чашку кофе на площадках банка Открытие. Для регистрации нажми /reg')

        def get_email(message): #получаем email
            global email
            email = message.text.lower()
            pattern = compile('(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
            is_valid = pattern.match(email)
            if is_valid:
                email_a = email.split('@')
                if email_a[1] == "open.ru":
                    global code
                    code = random.randint(1000,9999)
                    newCode(file_db, message.from_user.id, email, code)
                    send_code(email_smtp_server, email_login, email_pwd, email, code)
                    bot.send_message(message.from_user.id, 'На твою почту ' + email + ' был отправлен код подтверждения. Пожалуйста, введи его. Если ты ошибся при вводе e-mail, нажми /setemail')
                    bot.register_next_step_handler(message, get_check_pin)
                else:
                    bot.send_message(message.from_user.id, "Введи адрес своей почты email@open.ru")
                    bot.register_next_step_handler(message, get_email); #следующий шаг – функция get_email
            else:
                bot.send_message(message.from_user.id, "Введи адрес своей почты email@open.ru")
                bot.register_next_step_handler(message, get_email); #следующий шаг – функция get_email

        def get_check_pin(message): #проверяем Pin
            pin = message.text
            infoCode = getCode(file_db, message.from_user.id)
            if infoCode[4] == pin:
                bot.send_message(message.from_user.id, 'Теперь я могу тебе доверять =) Осталось нам с тобой познакомиться и можно будет попить кофейку ☕️. Введи свое имя.')
                bot.register_next_step_handler(message, get_name)

            elif message.text == '/setemail':
                deleteCode(file_db, message.from_user.id)
                bot.send_message(message.from_user.id, "Ок, будь внимательнее! Введи адрес своей корпоративной почты email@open.ru")
                bot.register_next_step_handler(message, get_email); #следующий шаг – функция get_email

            else:
                bot.send_message(message.from_user.id, 'Код неверный. Попробуй еще раз.')
                bot.register_next_step_handler(message, get_check_pin)


        def get_name(message): #получаем фамилию
            name = message.text
            addTempName(file_db, message.from_user.id, name)
            bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
            bot.register_next_step_handler(message, get_reg_end)


        def get_reg_end(message):
            surname = message.text
            name = getTempName(file_db, message.from_user.id)
            newUser(file_db, message.from_user.id, name, surname) #Добавляем пользователя в БД
            deleteCode(file_db, message.from_user.id)
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Да", callback_data="cb_yes"),
                                       InlineKeyboardButton("Пока не готов", callback_data="cb_no"))
            bot.send_message(message.from_user.id, "Ура! Вот мы и познакомились =) Пора попить кофе?", reply_markup=markup)


        #Обработка нажатия кнопок
        @bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):

            call_a = call.data.split('_')
            if call_a[0] == "cancel":
                delete_user_from_queue(file_db, call.from_user.id)
                bot.send_message(call.from_user.id, 'Ок, как будешь готов попить кофе, дай мне знать 😉')
            elif call.data == "stopchat_yes":
                bot.answer_callback_query(call.id, "Остановка диалога")
                if checkActiveDialog(file_db, call.from_user.id):
                    bot.send_message(getCompanionId(file_db, call.from_user.id), 'Диалог остановлен. Надеюсь все прошло хорошо, возвращайся снова! Если захочешь попить кофейку, напиши любое слово')
                    bot.send_message(call.from_user.id, 'Диалог остановлен. Надеюсь все прошло хорошо, возвращайся снова! Если захочешь попить кофейку, напиши любое слово')
                    disableDialog(file_db, call.from_user.id)
                    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
                else:
                    bot.send_message(call.from_user.id, 'В данный момент нет активных диалогов')
            elif call.data == "stopchat_no":
                bot.answer_callback_query(call.id, "Остановка диалога")
                if checkActiveDialog(file_db, call.from_user.id):
                    bot.send_message(call.from_user.id, 'Вы можете продолжить беседу')
                    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
                else:
                    bot.send_message(call.from_user.id, 'В данный момент нет активных диалогов')

            if not checkUserInQueue(file_db, call.from_user.id) and not checkActiveDialog(file_db, call.from_user.id): #Не реагируем на кнопки, если есть активный диалог или ожидание в очереди
                if call_a[0] == "town":
                    address = getLocationAddress(file_db, call_a[1])
                    markup = InlineKeyboardMarkup()
                    for row in address:
                        markup.add(InlineKeyboardButton(row[2], callback_data="gotoqueue_" + str(row[0])))
                    bot.send_message(call.from_user.id, "Выбери адрес или поделись геопозицией и я сам пойму где ты находишься 😏", reply_markup=markup)

                elif call_a[0] == "gotoqueue":
                    if checkUserInQueue(file_db, call.from_user.id):
                        utput = str("Я уже подыскиваю пару для тебя.")
                        bot.send_message(call.from_user.id, output)
                    else:
                        bot.answer_callback_query(call.id, "Поиск собеседника")
                        InfoByTelegramId = getInfoByTelegramId(file_db, call.from_user.id)
                        location_id = InfoByTelegramId['location_id']
                        location_info = getLocationInfo(file_db, location_id)
                        add_to_queue(file_db, call.from_user.id, location_id, 0, "")
                        output = str("Я добавил тебя в список желающих попить кофе по адресу {0}, {1}. Как только я найду пару, сразу сообщу.".format(location_info[1], location_info[2]))
                        bot.send_message(call.from_user.id, output)

                        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

                elif call_a[0] == "givephoto":
                    bot.answer_callback_query(call.id, "Приложи фото")
                    updateLocation(file_db, call.from_user.id, call_a[1])
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 2
                    markup.add(InlineKeyboardButton("Я не хочу загружать фото", callback_data="gotoqueue"))
                    bot.send_message(call.from_user.id, "Приложи свое селфи и я порекомендую тебе кофе и найду наиболее подходящего собеседника!", reply_markup=markup)


                elif call.data == "cb_nolocation":
                    bot.send_message(call.from_user.id, " Поделись геопозицией, чтобы я понял на какой площадке ты находишься 😏")


                elif call.data == "cb_yes":
                    bot.answer_callback_query(call.id, "Поделись геопозицией")
                    userInfo = getInfoByTelegramId(file_db, call.from_user.id)
                    if userInfo['location_id']:
                        location_info = getLocationInfo(file_db, userInfo['location_id'] )
                        location = str("Последний раз ты был на локации по адресу: {0}, {1}. Сейчас ты здесь?".format(location_info[1], location_info[2]))
                        markup = InlineKeyboardMarkup()
                        markup.row_width = 2
                        markup.add(InlineKeyboardButton("Да", callback_data="givephoto_" + str(userInfo['location_id'])),
                                                   InlineKeyboardButton("Нет", callback_data="cb_nolocation"))
                        bot.send_message(call.from_user.id, location, reply_markup=markup)

                    else:
                        bot.send_message(call.from_user.id, " Поделись геопозицией, чтобы я понял на какой площадке ты находишься 😏")

                elif call.data == "cb_no":
                    bot.answer_callback_query(call.id, "Ок, как будешь готов, пиши 😉")
                    bot.send_message(call.from_user.id, "Ок, как будешь готов, пиши 😉")

            else:
                if not checkActiveDialog(file_db, call.from_user.id) and call.data != "stopchat_no":
                    bot.answer_callback_query(call.id, "Кнопки не доступны")
                    bot.send_message(call.from_user.id, 'В данный момент эти кнопки не доступны')


        @bot.message_handler(content_types=['location'])
        def handle_docs_location(message):
            nl = nearestLocation(message.location.latitude, message.location.longitude)
            location = str("Ты находишься по адресу: {0}, {1}?".format(nl['location_town'], nl['location_address']))

            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Да", callback_data="givephoto_" + str(nl['location_id'])),
                                       InlineKeyboardButton("Нет", callback_data="cb_yes"))
            bot.send_message(message.from_user.id, location, reply_markup=markup)


        @bot.message_handler(content_types=['photo'])
        def handle_docs_photo(message):
            if not checkUserInQueue(file_db, message.from_user.id) and not checkActiveDialog(file_db, message.from_user.id):
                bot.send_message(message.from_user.id, "Анализирую твое фото...")
                try:
                    file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
                    downloaded_file = bot.download_file(file_info.file_path)

                    src=file_info.file_path;
                    with open("photos/" + str(message.from_user.id) + ".jpg", 'wb') as new_file:
                       new_file.write(downloaded_file)

                    azureInfo = getInfoByPhoto("https://westcentralus.api.cognitive.microsoft.com/face/v1.0/", ms_token,"./photos/"+ str(message.from_user.id) +".jpg")
                    bot.reply_to(message, azureInfo['text'])

                    InfoByTelegramId = getInfoByTelegramId(file_db, message.from_user.id)
                    location_id = InfoByTelegramId['location_id']
                    if location_id:
                        location_info = getLocationInfo(file_db, location_id)
                        add_to_queue(file_db, message.from_user.id, location_id, 1, azureInfo['faceId'])
                        output = str("Я добавил тебя в список желающих попить кофе по адресу {0}, {1}. Как только я найду пару, сразу сообщу.".format(location_info[1], location_info[2]))
                        bot.send_message(message.from_user.id, output)
                        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                    else:
                        output = "Пока я не понимаю, что мне делать с этим фото. Напиши что-нибудь, если хочешь выпить кофейку =)"
                        bot.send_message(message.from_user.id, output)
                        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)

                except Exception as e:
                    bot.reply_to(message, "Не удалось проанализировать фото" )
                    InfoByTelegramId = getInfoByTelegramId(file_db, message.from_user.id)
                    location_id = InfoByTelegramId['location_id']
                    if location_id:
                        location_info = getLocationInfo(file_db, location_id)
                        add_to_queue(file_db, message.from_user.id, location_id, 0, "")
                        output = str("Я добавил тебя в список желающих попить кофе по адресу {0}, {1}. Как только я найду пару, сразу сообщу.".format(location_info[1], location_info[2]))
                        bot.send_message(message.from_user.id, output)
                        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
                    else:
                        output = "Пока я не понимаю, что мне делать с этим фото. Напиши что-нибудь, если хочешь выпить кофейку =)"
                        bot.send_message(message.from_user.id, output)
                        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)

            elif checkActiveDialog(file_db, message.from_user.id): #Отправка изображений собеседнику
                file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src=file_info.file_path;
                with open("sent_images/" + str(message.from_user.id) + ".jpg", 'wb') as new_file:
                   new_file.write(downloaded_file)
                img=open("sent_images/" + str(message.from_user.id) + ".jpg",'rb')
                bot.send_message(getCompanionId(file_db, message.from_user.id), "Вам прислали изображение:")
                bot.send_photo(getCompanionId(file_db, message.from_user.id),img)

            else:
                output = "Пока я не понимаю, что мне делать с этим фото."
                bot.send_message(message.from_user.id, output)
                bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)

        bot.polling(none_stop=True, interval=0)


def timerFunc():
    def create_appointment(telegram_id_1, telegram_id_2, photo_flag_1, photo_flag_2, queue_id_1, queue_id_2, location_id):
        info_user_1 = getUserInfo(file_db, telegram_id_1)
        info_user_2 = getUserInfo(file_db, telegram_id_2)
        bot.send_message(telegram_id_1, str("Ура! Ты идешь пить кофе с сотрудником {0}!".format(info_user_2[2])))
        bot.send_message(telegram_id_2, str("Ура! Ты идешь пить кофе с сотрудником {0}!".format(info_user_1[2])))
        if photo_flag_2 == 1:
          img=open("photos/" + str(telegram_id_2) + ".jpg",'rb')
          bot.send_photo(telegram_id_1,img)
        if photo_flag_1 == 1:
          img=open("photos/" + str(telegram_id_1) + ".jpg",'rb')
          bot.send_photo(telegram_id_2,img)
        bot.send_message(telegram_id_1, str("Далее ты продолжаешь диалог с сотрудником {0}, договоритесь о времени и месте встречи! Чтобы остановить диалог, в любой момент нажми /stopchat. Чтобы найти места с кофе поблизости, нажми /showcs. Хорошей беседы!".format(info_user_2[2])))
        bot.send_message(telegram_id_2, str("Далее ты продолжаешь диалог с сотрудником {0}, договоритесь о времени и месте встречи! Чтобы остановить диалог, в любой момент нажми /stopchat. Чтобы найти места с кофе поблизости, нажми /showcs. Хорошей беседы!".format(info_user_1[2])))
        add_to_couple(file_db, telegram_id_1, telegram_id_2, location_id) #Добавление пары в таблицу
        delete_from_queue(file_db, queue_id_1, queue_id_2) #Удаление пользователей из очереди

    def searchCouples():
        conn = sqlite3.connect(file_db)
        cursor = conn.cursor()
        #Отбираем локации, в которых стоит более 1 в очереди
        cursor.execute('SELECT location_id FROM queue GROUP BY location_id HAVING COUNT(*) > 1')
        data_locations = cursor.fetchall()
        if len(data_locations) > 0:
            for location_id in data_locations: #Перебираем все локации, где в очереди стоят больше 1 человека
                i = True
                while i is True:
                    #определяем количество в очереди
                    cursor.execute('SELECT * FROM queue WHERE location_id=' + str(location_id[0]))
                    data_people = cursor.fetchall()
                    if len(data_people) > 2: # Если больше 2, то отбираем всех с фото
                        cursor.execute('SELECT * FROM queue WHERE photo_flag="1" AND location_id=' + str(location_id[0]))
                        data_people_photo = cursor.fetchall()
                        if len(data_people_photo) > 2: # Если больше 2, то сравниваем схожесть
                            face_id = data_people_photo[0][5]
                            face_ids = []
                            for person in data_people_photo:
                                if person[5] != face_id:
                                    face_ids.append(person[5])
                            face_id_second = useFaceApiFindSimilar("https://westcentralus.api.cognitive.microsoft.com/face/v1.0/findsimilars",ms_token,face_id,face_ids)
                            cursor.execute('SELECT * FROM queue WHERE face_id IN ("'+face_id+'", "'+face_id_second['faceId']+'")')
                            data = cursor.fetchall()
                            create_appointment(data[0][2], data[1][2], data[0][4], data[1][4], data[0][0], data[1][0], data[0][3])
                        elif len(data_people) == 2: #Если только двое с фотками, то сводим их
                            create_appointment(data_people_photo[0][2],
                                                data_people_photo[1][2],
                                                data_people_photo[0][4],
                                                data_people_photo[1][4],
                                                data_people_photo[0][0],
                                                data_people_photo[1][0],
                                                data_people_photo[0][3])
                        else: #Если меньше двух с фотками, ты сводим людей без фильтра по фоткам
                            create_appointment(data_people[0][2], data_people[1][2], data_people[0][4], data_people[1][4], data_people[0][0], data_people[1][0], data_people[0][3])

                    elif len(data_people) == 2: #Сводим двоих
                        data = cursor.fetchall()
                        create_appointment(data_people[0][2], data_people[1][2], data_people[0][4], data_people[1][4], data_people[0][0], data_people[1][0], data_people[0][3])

                    else:
                        i = False

        #Проверка времени нахождения в очереди
        cursor.execute('SELECT * FROM queue')

        a = datetime.datetime.now()
        for row in cursor.fetchall():
            b = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            c = a - b - datetime.timedelta(minutes=180)
            if c.seconds/60 > 30:
                cursor.execute(str("DELETE FROM queue WHERE queue_id = '{0}'".format(str(row[0]))))
                conn.commit()
                bot.send_message(row[2], "К сожалению, пару для кофепития найти не удалось. Попробуй еще раз!")

    searchCouples()


def setInterval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop(): # executed in another thread
                while not stopped.wait(interval): # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator


#Запускаем потоки с поллером телеграма и таймером
if __name__ == '__main__':
    #Запускаем поток с таймером
    @setInterval(5)
    def function():
        timerFunc()
    stop = function()

    #Запускаем поток с поллером телеграмма и функциями диалога
    cbClassp = cbClass()
    Thread(target = cbClassp.cbFunc()).start()
