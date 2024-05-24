import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from app.routes.cards_collection import create_user_card_relationship

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()
    
    for document in mongo["users"].find():
        id = document.get('_id')
        
        query = {"name": {"$exists": True}}
        
        sample_size = 2000
        pipeline = [
            {'$match': query},
            {'$sample': {'size': sample_size}}
        ]


        random_cards = list(mongo['cards'].aggregate(pipeline))
        for card in random_cards:
            card_id = card.get('_id')
            foundCollection = mongo['cards_collection'].find_one({ "user_id": id })
            if foundCollection == None:
                mongo['cards_collection'].insert_one({ "user_id": id, "cards_id": [card_id] })
            else:
                mongo['cards_collection'].update_one({ "user_id": id}, {'$push': { 'cards_id': {'$each': [card_id] }}})
    
    for document in mongo["cards_collection"].find():
        user_id = str(document.get('user_id'))
        cards_id = document.get('cards_id')
        

        for card_id in cards_id:
            create_user_card_relationship(user_id=user_id, card_id=card_id)
