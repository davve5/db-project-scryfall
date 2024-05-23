import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()

    for document in mongo["users"].find():
        id = str(document.get('_id'))
        username = document.get('username')
        query = "CREATE (n:User {id: $id, username: $username})"
        neo4j.run(query, {"id": str(id), "username": username})
        

