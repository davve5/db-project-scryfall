import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from app.routes.cards_collection import create_user_card_relationship

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()

    for document in mongo["cards_collection"].find():
        user_id = str(document.get('user_id'))
        cards_id = document.get('cards_id')
        

        for card_id in cards_id:
            create_user_card_relationship(user_id=user_id, card_id=card_id)
