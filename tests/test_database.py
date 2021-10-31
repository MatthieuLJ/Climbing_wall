

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

def test_all_holds_positions():
    db_file = database.create_database()

    db_conn = database.get_db_connection()
    cursor = db_conn.cursor()

    assert database.get_all_holds_positions() == []

    cursor.execute("INSERT INTO holds (id,x,y) VALUES (1,10,10)")
    cursor.execute("INSERT INTO holds (id,x,y) VALUES (2,20,20)")
    cursor.execute("INSERT INTO holds (id,x,y) VALUES (4,40,40)")
    cursor.execute("INSERT INTO holds (id,x,y) VALUES (3,30,30)")
    db_conn.commit()

    list_with_positions = [[1,10,10],[2,20,20],[3,30,30],[4,40,40]]
    print(str(database.get_all_holds_positions()))

    assert database.get_all_holds_positions() == list_with_positions

    os.remove(db_file)


def test_shortest_distance():
    db_file = database.create_database()

    db_conn = database.get_db_connection()
    cursor = db_conn.cursor()

    assert database.get_all_holds_positions() == []

    cursor.execute("INSERT INTO holds (id,x,y) VALUES (1,10,10)")
    cursor.execute("INSERT INTO holds (id,x,y) VALUES (2,10,20)")
    db_conn.commit()

    assert database.get_shortest_distance() == 10

    cursor.execute("INSERT INTO holds (id,x,y) VALUES (3,20,10)")
    db_conn.commit()

    assert database.get_shortest_distance() == 10

    cursor.execute("INSERT INTO holds (id,x,y) VALUES (4,10,15)")
    db_conn.commit()

    assert database.get_shortest_distance() == 5

    db_conn.commit()