
# Use ":memory:" databases to test

import database
import os
import sqlite3
import tempfile

def test_create_and_initialize_db():
    db_file = database.create_database()
    assert os.path.exists(db_file)

    db_conn = sqlite3.connect(db_file)
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='holds';")
    assert len(cursor.fetchall()) == 1

    assert database.get_num_holds() == 0

    database.set_hold_position(0, 10, 10)
    
    assert database.get_num_holds() == 1

    # Moving the database somewhere else
    new_file = tempfile.NamedTemporaryFile(suffix=".db", dir = os.getcwd(), delete=False)
    os.rename(db_file, new_file.name)

    database.initialize_db(new_file.name)
    assert database.get_num_holds() == 1
    os.remove(new_file.name)
    