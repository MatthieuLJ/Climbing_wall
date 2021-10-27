from sqlite3.dbapi2 import Cursor
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import imghdr
import json

import os.path

from tornado.options import define, options

import configuration
import database
import lights
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
            (r"/set_num_holds", SetNumHoldsHandler),
            (r"/set_hold_coords", SetHoldCoordsHandler),
            (r"/", IndexHandler)
        ]

        tornado.web.Application.__init__(self, handlers, static_path=os.path.join(os.path.dirname(__file__),'static'))

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        global current_state
        print("current state: "+str(current_state))
        if current_state == State.INITIALIZING:
            return self.write_error(503)
        elif current_state == State.NO_WALL:
            return self.redirect("/new_wall")
        elif current_state == State.EMPTY_WALL or current_state == State.CONFIGURING_WALL:
            return self.redirect("/configure_wall")
        elif current_state == State.READY:
            return self.render("templates/top_menu.html")

class ConfigureWallHandler(tornado.web.RequestHandler):
    def get(self):
        if current_state == State.EMPTY_WALL:
            self.render("templates/wall_num_holds.html", wall_image=configuration.get_wall_file())
        elif current_state == State.CONFIGURING_WALL:
            set_next_light_to_configure()
            self.render("templates/wall_set_holds.html", wall_image=configuration.get_wall_file())
        else:
            self.redirect("/")

class NewWallHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/welcome_upload_image.html")

class WallUploadHandler(tornado.web.RequestHandler):
    def post(self):
        global current_state
        self.set_header("Content-Type", 'application/json')

        wall = self.request.files['wall'][0]
        extension = os.path.splitext(wall['filename'])[1]
        final_filename= "static/wall"+extension

        with open(final_filename, 'wb') as output_file:
            output_file.write(wall['body'])

        if imghdr.what(final_filename) is None:
            os.remove(final_filename)
            current_state = State.NO_WALL
            print("This is not a valide image")
            return self.write(json.dumps({'redirect': False, 'error': "this is not a valid image"}))

        configuration.set_wall_file(final_filename)
        current_state = State.EMPTY_WALL

        return self.write(json.dumps({'redirect': True, 'url': "/configure_wall"}))

class SetNumHoldsHandler(tornado.web.RequestHandler):
    def post(self):
        global current_state
        self.set_header("Content-Type", 'application/json')

        if current_state == State.EMPTY_WALL:
            # Check if we got a real number
            num_holds = self.get_argument('num_holds')
            if not num_holds.isdigit() or int(num_holds) == 0:
                return self.write(json.dumps({'redirect': False}))

            configuration.set_num_holds(int(num_holds))
            lights.set_num_lights(int(num_holds))
            database.clear_holds()
            print("Set the number of holds to " + str(configuration.get_num_holds()))
            current_state = State.CONFIGURING_WALL
            return self.write(json.dumps({'redirect': True, 'url': "/configure_wall"}))
        else:
            return self.write(json.dumps({'redirect': True, 'url': "/"}))

class SetHoldCoordsHandler(tornado.web.RequestHandler):
    def post(self):
        global current_state
        self.set_header("Content-Type", 'application/json')

        coord_x = self.get_argument('x')
        coord_y = self.get_argument('y')
        database.set_hold_position(database.get_minimum_index_unknown_light(), coord_x, coord_y)
        if database.get_minimum_index_unknown_light() > configuration.get_num_holds():
            lights.clear_all()
            current_state = State.READY
            return self.write(json.dumps({'redirect': True, 'url': "/"}))
        else:
            set_next_light_to_configure()
            return self.write(json.dumps({'redirect': False}))

def set_next_light_to_configure():
    lights.clear_all()
    index = database.get_minimum_index_unknown_light()
    lights.set_light(index, (255,255,255))

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
            lights.set_num_lights(num_holds)
            if database.get_minimum_index_unknown_light() < num_holds:
                current_state = State.CONFIGURING_WALL
            else:
                current_state = State.READY

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()