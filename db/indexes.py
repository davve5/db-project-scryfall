from pymongo import ASCENDING, TEXT
from db.mongo import MongoManager
from db.neo4j import Neo4jManager

def create_indexes():
    mongo = MongoManager.get_instance()
    mongo['users'].create_index([('username', ASCENDING)], unique=True)

    mongo['cards'].create_index([('name', TEXT)])
    mongo['cards'].create_index([('color_identity', ASCENDING)], sparse=True)
    mongo['cards'].create_index([('rarity', ASCENDING)], sparse=True)
    mongo['cards'].create_index([('type_line', ASCENDING)], sparse=True)
    mongo['cards'].create_index([('legalities', ASCENDING)], sparse=True)
    mongo['cards'].create_index([('set_type', ASCENDING)], sparse=True)
    mongo['cards'].create_index([('power', ASCENDING)], sparse=True)
    mongo['cards'].create_index([('toughness', ASCENDING)], sparse=True)
    mongo['cards'].create_index([('mana_cost', ASCENDING)], sparse=True)

    mongo['decks'].create_index([('name', TEXT)])

    neo4j = Neo4jManager.get_instance()
    neo4j.run("CREATE INDEX user_id IF NOT EXISTS FOR (u:User) ON (u.id)")
    
    neo4j.run("CREATE INDEX card_id IF NOT EXISTS FOR (c:Card) ON (c.id)")
    neo4j.run("CREATE INDEX card_type_line IF NOT EXISTS FOR (c:Card) ON (c.type_line)")
    neo4j.run("CREATE INDEX card_name IF NOT EXISTS FOR (c:Card) ON (c.name)")

    neo4j.run("CREATE INDEX deck_id IF NOT EXISTS FOR (d:Deck) ON (d.id)")
