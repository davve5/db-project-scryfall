import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from pymongo import MongoClient

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()

    json_path = 'seeders/json_files/mtg.cards.json'


    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
        
        if isinstance(data, dict):
            data = [data]
        
        mongo["cards"].insert_many(data)


    for document in mongo["cards"].find():
        id = str(document.get('_id'))
        name = document.get('name')
        type_line = document.get('type_line')
        rarity = document.get('rarity')
        colors = document.get('colors', [])

        query = "CREATE (n:Card {id: $id, name: $name, type_line: $type_line, rarity: $rarity, colors: $colors})"
        neo4j.run(query, {"id": id, "name": name, "type_line": type_line, "colors":colors, "rarity":rarity})
