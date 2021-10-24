from enum import Enum

class State(Enum):
    INITIALIZING = -1
    READY = 0

    NO_WALL = 1           # We do not know what the wall looks like
    EMPTY_WALL = 2        # We do not know how many climbing holds
    CONFIGURING_WALL = 3  # We do not know where the climbing holds are

    CREATING_ROUTE = 10
    CUSTOM_LIGHTS = 11
    LOADING_ROUTES = 12

    CUSTOM_MODE_STARRY_NIGHT = 50
    CUSTOM_MODE_MESSAGE = 51