import json
from db.mongo import MongoManager

def up():
		mongo = MongoManager.get_instance()

		users = [
			{ "login": "dawid", "password": "12345678"},
			{ "login": "dominik", "password": "12345678"}
		]

		mongo['users'].insert_many(users)