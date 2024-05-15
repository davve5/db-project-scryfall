import os
from pymongo import MongoClient, database

class MongoManager:
   __instance:  | None = None
   
   @staticmethod 
   def get_instance() -> database.Database:
      if MongoManager.__instance == None:
            MongoManager()
      return MongoManager.__instance
   def __init__(self):
      if MongoManager.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         MongoManager.__instance = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/"))[os.getenv("MONGODB_DB_NAME", "mgt")]