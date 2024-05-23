import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from app.routes.decks import create_user_deck_relationship, create_deck, create_deck_card_relationship

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()

    for document in mongo["decks"].find():
        id = str(document.get('_id'))
        name = document.get('name')
        user_id = str(document.get('user_id'))
        cards_id = document.get('cards_id')
        
        create_deck(id=id, name=name)
        create_user_deck_relationship(user_id=user_id, deck_id=id)

        for card_id in cards_id:
            create_deck_card_relationship(deck_id=id, card_id=card_id)
