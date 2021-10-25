

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


def test_lowest_unused_index():
    db_file = database.create_database()

    db_conn = database.get_db_connection()
    cursor = db_conn.cursor()

    assert database.get_minimum_index_unknown_light() == 1

    cursor.execute("INSERT INTO holds (id) VALUES (2)")
    db_conn.commit()

    assert database.get_minimum_index_unknown_light() == 1

    cursor.execute("INSERT INTO holds (id) VALUES (3)")
    db_conn.commit()

    assert database.get_minimum_index_unknown_light() == 1

    cursor.execute("INSERT INTO holds (id) VALUES (1)")
    db_conn.commit()

    assert database.get_minimum_index_unknown_light() == 4

    cursor.execute("INSERT INTO holds (id) VALUES (5)")
    db_conn.commit()

    assert database.get_minimum_index_unknown_light() == 4

    os.remove(db_file)