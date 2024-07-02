import os
import json


################ Configuration ##################

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def get_username(user_id):
    config = load_config()
    return config.get(user_id)


def save_username(user_id, username):
    config = load_config()
    config[user_id] = username
    save_config(config)
