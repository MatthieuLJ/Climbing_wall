import os
import sqlite3
import tempfile

from sqlite3 import Error


db_filename = ""

def create_db_tables(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS holds (
        id INTEGER PRIMARY KEY,
        x INTEGER,
        y INTEGER,
        brightness INTEGER );""")

def get_db_connection():
    global db_filename

    # Initialize database
    try:
        db_conn = sqlite3.connect(db_filename)
    except Error as e:
        print(e)
        return None

    return db_conn

def create_database():
    global db_filename

    # get a random file name
    db_file = tempfile.NamedTemporaryFile(suffix=".db", dir = os.getcwd(), delete=False)
    db_filename = db_file.name
    print(db_filename)
    db_conn = get_db_connection()
    create_db_tables(db_conn)

    return db_filename

def initialize_db(filename):
    global db_filename
    db_filename = filename

    db_conn = get_db_connection()
    if db_conn is None:
        return None

    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='holds';")
    if len(cursor.fetchall()) == 0:
        create_db_tables(db_conn)

def get_num_holds():
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM holds;")
    num_holds = cursor.fetchall()
    if len(num_holds) == 0:
        return None
    else:
        return num_holds[0][0]

def clear_holds():
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM holds;")

def set_hold_position(index, x, y):
    print("setting hold#"+str(index)+" at ("+str(x)+","+str(y))
    db_conn = get_db_connection()

    cursor = db_conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO holds (id, x, y, brightness) VALUES(?,?,?,?);", (index,x,y,100))
    db_conn.commit()

def get_hold_position(index):
    db_conn = get_db_connection()

    cursor = db_conn.cursor()
    cursor.execute("SELECT x,y FROM holds WHERE id=?;", (index,))
    position = cursor.fetchall()
    if len(position) == 0:
        return None
    else:
        return position[0]

def get_minimum_index_unknown_light():
    db_conn = get_db_connection()

    cursor = db_conn.cursor()
    cursor.execute("""SELECT min(unused) AS unused
                    FROM (
                        SELECT MIN(t1.id)+1 as unused
                        FROM holds AS t1
                        WHERE NOT EXISTS (SELECT * FROM holds AS t2 WHERE t2.id = t1.id+1)
                        UNION
                        SELECT 1
                        WHERE NOT EXISTS (SELECT * FROM holds WHERE id = 1)
                    ) AS subquery""")
    index = cursor.fetchall()
    if len(index) == 0:
        return None
    else:
        return index[0][0]
