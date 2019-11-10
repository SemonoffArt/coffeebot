# Вспомогательный файл для создания таблиц в БД
import sqlite3

conn = sqlite3.connect("cb.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()

def cr_t_people():
    cursor.execute("""CREATE TABLE people (
                person_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id,
                first_name TEXT,
                last_name TEXT,
                location_id TEXT,
                TIMESTAMP TEXT
                )
               """)
def cr_t_locations():
    cursor.execute("""CREATE TABLE locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_town TEXT,
                location_address TEXT,
                location_longitude TEXT,
                location_latitide TEXT
                )
               """)
    #Добавление локаций
    '''
    locations = [('Москва', 'ул. Электрозаводская, 27, стр. 8', '37.70560749999999', '55.79158206894956'),
              ('Москва', 'ул. Электрозаводская, 27, стр. 9', '37.707026499999984', '55.791349068948946'),
              ('Москва', 'ул. Летниковская, 2, стр. 3', '37.64340799999999', '55.72898606902708')]

    cursor.executemany("INSERT INTO locations (location_town, location_address, location_longitude, location_latitide) VALUES (?,?,?,?)", locations)
    conn.commit()
    '''

def cr_t_queues():
    cursor.execute("""CREATE TABLE queue (
                queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
                TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                telegram_id TEXT,
                location_id TEXT,
                photo_flag INT,
                face_id TEXT
                )
               """)

def cr_t_couples():
    cursor.execute("""DROP TABLE couples""")
    cursor.execute("""CREATE TABLE couples (
                couple_id INTEGER PRIMARY KEY AUTOINCREMENT,
                TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                telegram_id_1 TEXT,
                telegram_id_2 TEXT,
                location_id TEXT,
                active_dialog INT
                )
               """)
def cr_t_codes():
    cursor.execute("""CREATE TABLE codes (
                code_id INTEGER PRIMARY KEY AUTOINCREMENT,
                TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
                telegram_id TEXT,
                email TEXT,
                code TEXT,
                tmp_name TEXT
                )
               """)
