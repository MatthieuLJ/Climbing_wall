from sqlite3.dbapi2 import Cursor
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import imghdr

import os.path

from tornado.options import define, options

import database
from state import State

define("port", default=8888, help="run on the given port", type=int)

current_state = State.INITIALIZING

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/new_wall", NewWallHandler),
            (r"/upload_wall", WallUploadHandler),
            (r"/configure_wall", ConfigureWallHandler),
            (r"/", IndexHandler)
        ]

        tornado.web.Application.__init__(self, handlers, static_path=os.path.join(os.path.dirname(__file__),'static'))

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        global current_state
        if current_state == State.INITIALIZING:
            return self.write_error(503)
        elif current_state == State.NO_WALL:
            return self.redirect("/new_wall")
        elif current_state == State.EMPTY_WALL:
            return self.redirect("/configure_wall")

class ConfigureWallHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish("Going to setup some wall")

class NewWallHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/welcome_upload_image.html")

class WallUploadHandler(tornado.web.RequestHandler):
    def post(self):
        global current_state
        print("uploading...")
        wall = self.request.files['wall'][0]
        extension = os.path.splitext(wall['filename'])[1]
        final_filename= "wall"+extension
        output_file = open(final_filename, 'wb')
        output_file.write(wall['body'])
        output_file.close()

        if imghdr.what(final_filename) is None:
            os.remove(final_filename)
            current_state = State.NO_WALL
            self.finish("file" + final_filename + " is not a valid image")
            return

        db_conn = database.get_db_connection()
        cursor = db_conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO info VALUES('wall_image', '"+final_filename+"');")
        db_conn.commit()
        print("executed" + "INSERT OR REPLACE INTO info VALUES('wall_image', '"+final_filename+"');")

        self.redirect("/configure_wall")

def main():
    global current_state

    current_state = database.initialize_db()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()