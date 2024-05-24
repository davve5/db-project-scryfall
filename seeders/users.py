import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from app.routes.auth import get_password_hash
import random

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()
    password = "password"
    
    for i in range (7):
        username = "user" + str(i)
        hashed_password = get_password_hash(password)
        mongo["users"].insert_one({"username": username, "hashed_password": hashed_password})
    

    for document in mongo["users"].find():
        id = str(document.get('_id'))
        username = document.get('username')
        query = "CREATE (n:User {id: $id, username: $username})"
        neo4j.run(query, {"id": str(id), "username": username})
        

