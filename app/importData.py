from pymongo import MongoClient
from neo4j import GraphDatabase

mongo_client = MongoClient('localhost', 27017)
mongo_db = mongo_client['mtg']
mongo_collection = mongo_db['cards']

neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jgraph"))
neo4j_session = neo4j_driver.session()

def importData():
    for document in mongo_collection.find():
        name = document.get('name')
        released_at = document.get('released_at')
        type_line = document.get('type_line')
        rarity = document.get('rarity')
        colors = document.get('colors', [])
        #prices = document.get('prices', [])

        query = "CREATE (n:Card {name: $name, released_at: $released_at, type_line: $type_line, rarity: $rarity, colors: $colors})"
        neo4j_session.run(query, {"name": name, "released_at": released_at, "type_line": type_line, "colors":colors, "rarity":rarity})

importData()

neo4j_session.close()
neo4j_driver.close()
mongo_client.close()