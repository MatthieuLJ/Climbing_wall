import json


config_file = "config.json"

config = {}

# {
#   wall_file: "whateverfile.jpn",
#   number_holds: 250,
#   database_file: "my_database.sqlite",
# }

def load_config():
    global config_file
    global config

    with open(config_file, 'r') as f:
        config = json.load(f)

def save_config():
    global config_file
    global config
    
    with open(config_file, 'w') as f:
        json.dump(config, f)

def set_num_holds(num):
    global config
    config["number_holds"] = num
    save_config()

def get_num_holds():
    global config
    if "number_holds" in config:
        return config["number_holds"]
    else:
        return None

def set_wall_file(file_name):
    global config
    config["wall_file"] = file_name
    save_config()

def get_wall_file():
    global config
    if "wall_file" in config:
        return config["wall_file"]
    else:
        return None

def set_db_file(file_name):
    global config
    config["database_file"] = file_name
    save_config()

def get_db_file():
    global config
    if "database_file" in config:
        return config["database_file"]
    else:
        return None