from sqlite3.dbapi2 import Cursor
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import imghdr

import os.path

from tornado.options import define, options

import configuration
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
        self.render("templates/wall_creation.html", wall_image=configuration.get_wall_file(), instructions = "How many holds?")

class NewWallHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/welcome_upload_image.html")

class WallUploadHandler(tornado.web.RequestHandler):
    def post(self):
        global current_state
        wall = self.request.files['wall'][0]
        extension = os.path.splitext(wall['filename'])[1]
        final_filename= "static/wall"+extension

        with open(final_filename, 'wb') as output_file:
            output_file.write(wall['body'])

        if imghdr.what(final_filename) is None:
            os.remove(final_filename)
            current_state = State.NO_WALL
            self.finish("file" + final_filename + " is not a valid image")
            return

        configuration.set_wall_file(final_filename)
        current_state = State.EMPTY_WALL

        self.redirect("/configure_wall")

def main():
    global current_state

    current_state = State.INITIALIZING

    configuration.load_config()
    if configuration.get_db_file() is None:
        db_file = database.create_database()
        configuration.set_db_file(db_file)
    else:
        database.initialize_db(configuration.get_db_file())

    if configuration.get_wall_file() is None:
        current_state = State.NO_WALL
    else:
        wall_image = configuration.get_wall_file()
        
        if not os.path.exists(wall_image) or imghdr.what(wall_image) is None:
            current_state = State.NO_WALL
        elif configuration.get_num_holds() is None or configuration.get_num_holds() == 0:
            current_state = State.EMPTY_WALL
        else:
            num_holds = configuration.get_num_holds()
            if database.get_num_holds() < num_holds:
                current_state = State.CONFIGURING_WALL
            else:
                current_state = State.READY


    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()