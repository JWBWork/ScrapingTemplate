import json
from os import path

config_path = path.join(path.dirname(__file__), '../config.json')
with open(config_path) as config_file:
	config = json.load(config_file)
