from sqlite3.dbapi2 import Cursor
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import sqlite3
from sqlite3 import Error

import imghdr

import os.path
import sys

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/new_wall", NewWallHandler),
            (r"/upload_wall", WallUploadHandler),
            (r"/configure_wall", ConfigureWallHandler),
            (r"/", IndexHandler)
        ]
        tornado.web.Application.__init__(self, handlers)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        pass

class ConfigureWallHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish("Going to setup some wall")

class NewWallHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("welcome_upload_image.html")

class WallUploadHandler(tornado.web.RequestHandler):
    def post(self):
        print("uploading...")
        wall = self.request.files['wall'][0]
        extension = os.path.splitext(wall['filename'])[1]
        final_filename= "wall"+extension
        output_file = open(final_filename, 'wb')
        output_file.write(wall['body'])
        output_file.close()

        if imghdr.what(final_filename) is None:
            os.remove(final_filename)
            no_wall = True
            self.finish("file" + final_filename + " is not a valid image")
            return

        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO info VALUES('wall_image', '"+final_filename+"');")
        db_conn.commit()
        print("executed" + "INSERT OR REPLACE INTO info VALUES('wall_image', '"+final_filename+"');")
        no_wall = False
        empty_wall = True

        self.redirect("/configure_wall")

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
        no_wall = True
        return
    
    wall_image = wall_image[0][0]
    print("checking for file "+str(wall_image))
    if not os.path.exists(wall_image):
        no_wall = True
        return
    
    no_wall = False

    cursor.execute("SELECT * FROM holds;")
    empty_wall = (len(cursor.fetchall()) == 0)
    
def main():
    initialize_db()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()