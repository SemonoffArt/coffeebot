import sqlite3
import time
import datetime

def checkUserInQueue(file_db, telegram_id): #Проверка пользователся на нахождение в очереди
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM queue WHERE telegram_id = "' + str(telegram_id) + '"')
    data = cursor.fetchone()
    if data == None:
        return False
    else:
        return True


#Новый пользователь
def newUser(file_db, telegram_id, first_name, last_name):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO people (telegram_id, first_name, last_name, TIMESTAMP) VALUES (?,?,?,?)", (str(telegram_id), first_name, last_name, str(st)))
    conn.commit()


#Добавление нового кода регистрации в БД
def newCode(file_db, telegram_id, email, code):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO codes (telegram_id, email, code) VALUES (?,?,?)", (str(telegram_id), email, str(code)))
    conn.commit()


#Проверка пользователя на наличие регистрации
def getCode(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM codes WHERE telegram_id = "' + str(telegram_id) + '"')
    data = cursor.fetchone()
    return data


#Проверка пользователя на наличие регистрации
def checkUser(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM people WHERE telegram_id = "' + str(telegram_id) + '"')
    data = cursor.fetchone()
    if data == None:
        return False
    else:
        return data[2]


#Удаление кода
def deleteCode(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM codes WHERE telegram_id=" + str(telegram_id))
    conn.commit()
    return

#Добавление имени во временную таблицу
def addTempName(file_db, telegram_id, name):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE codes SET tmp_name=? WHERE telegram_id=?", (str(name), str(telegram_id)))
    conn.commit()
    return

#Добавление имени во временную таблицу
def getTempName(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM codes WHERE telegram_id = "' + str(telegram_id) + '"')
    data = cursor.fetchone()
    if data == None:
        return False
    else:
        return data[5]

#Получение списка городов
def getLocationTowns(file_db):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT location_town FROM locations')
    data = cursor.fetchall()
    return data

#Получение списка адресов
def getLocationAddress(file_db, town):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM locations WHERE location_town = "' + town + '"')
    data = cursor.fetchall()
    return data

#Получение инфы по локации
def getLocationInfo(file_db, location_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM locations WHERE location_id = "' + location_id + '"')
    data = cursor.fetchone()
    return data

#Добавление сотрудника в очередь
def add_to_queue(file_db, telegram_id, location_id, photo_flag, face_id):
    if not checkUserInQueue(file_db, telegram_id):
        conn = sqlite3.connect(file_db)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO queue (telegram_id, location_id, photo_flag, face_id) VALUES (?,?,?,?)", (str(telegram_id), str(location_id), photo_flag, face_id))
        conn.commit()
    return

#Удаление сотрудника из очереди
def delete_user_from_queue(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute(str("DELETE FROM queue WHERE telegram_id = '{0}'".format(str(telegram_id))))
    conn.commit()
    return

#Проверка статуса диалога
def checkActiveDialog(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM couples WHERE (telegram_id_1 = "' + str(telegram_id) + '" OR telegram_id_2 = "' + str(telegram_id) + '") AND active_dialog=1')
    data = cursor.fetchone()
    return data

#Получение  id компаньона
def getCompanionId(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM couples WHERE (telegram_id_1 = "' + str(telegram_id) + '" OR telegram_id_2 = "' + str(telegram_id) + '") AND active_dialog=1')
    data = cursor.fetchone()
    if data[2] == str(telegram_id):
        return data[3]
    else:
        return data[2]

#Остановка диалога
def disableDialog(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE couples SET active_dialog=0 WHERE (telegram_id_1=? OR telegram_id_2=?) AND active_dialog=1", (str(telegram_id), str(telegram_id)))
    conn.commit()
    return

#Получение инфо о сотруднике
def getInfoByTelegramId(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM people WHERE telegram_id = "' + str(telegram_id) + '"')
    data = cursor.fetchone()
    return {
        'name': data[2],
        'location_id': data[5]
    }

#Обновление локации у сотрудника
def updateLocation(file_db, telegram_id, location_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE people SET location_id=? WHERE telegram_id=?", (str(location_id), str(telegram_id)))
    conn.commit()
    return

#Объединение сотрудников в пару
def add_to_couple(file_db, telegram_id_1, telegram_id_2, location_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO couples (telegram_id_1, telegram_id_2, location_id, active_dialog) VALUES (?,?,?,?)", (str(telegram_id_1), str(telegram_id_2), str(location_id), 1))
    conn.commit()
    return

#Удаление сотрудников из очереди
def delete_from_queue(file_db, queue_id_1, queue_id_2):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute(str("DELETE FROM queue WHERE queue_id IN ({0}, {1})".format(queue_id_1, queue_id_2)))
    conn.commit()
    return

#Получение инфо о сотруднике
def getUserInfo(file_db, telegram_id):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM people WHERE telegram_id = "' + str(telegram_id) + '"')
    return cursor.fetchone()
