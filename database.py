import os
import sqlite3
import sys

from sqlite3 import Error

from state import State

def create_db_tables(db_conn):
    create_tables = ["""CREATE TABLE IF NOT EXISTS holds (
        id INTEGER PRIMARY KEY,
        x INTEGER,
        y INTEGER,
        brightness INTEGER );""",

        """CREATE TABLE IF NOT EXISTS info (
        label TEXT PRIMARY KEY,
        value TEXT );""",
    ]
    cursor = db_conn.cursor()
    try:
        for table in create_tables:
            cursor.execute(table)
    except Error as e:
        print(e)
        sys.exit(-1)

def get_db_connection():
    # Initialize database
    try:
        db_conn = sqlite3.connect("wall.db")
    except Error as e:
        print(e)
        sys.exit(-1)

    return db_conn

def initialize_db():
    db_conn = get_db_connection()

    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='holds';")
    if len(cursor.fetchall()) == 0:
        create_db_tables(db_conn)

    cursor.execute("SELECT value FROM info WHERE label='wall_image';")
    wall_image = cursor.fetchall()
    if len(wall_image) == 0:
        return State.NO_WALL
    
    wall_image = wall_image[0][0]
    print("checking for file "+str(wall_image))
    if not os.path.exists(wall_image):
        # TODO: delete the DB entry
        return State.NO_WALL

    cursor.execute("SELECT * FROM holds;")
    if len(cursor.fetchall()) == 0:
        return State.EMPTY_WALL

    return State.READY
