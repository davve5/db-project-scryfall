import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from app.routes.decks import create_user_deck_relationship, create_deck, create_deck_card_relationship
import random

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()

    for i in range(40):
        target_color = ['R', 'G', 'U', 'B', 'W', ]
        
        random_color = random.choice(target_color)
        
        query = {'colors': {'$in': [random_color]}}


        sample_size = 40
        pipeline = [
            {'$match': query},
            {'$sample': {'size': sample_size}}
        ]


        random_cards = list(mongo['cards'].aggregate(pipeline))
        
        
        
        random_user = "user" + str(random.randint(0, 6))
        
        deck_name = random_user + random_color +str(random.randint(0,256))
        
        
        query = {'username': {'$in': [random_user]}}
        
        sample_size = 1
        pipeline = [
            {'$match': query},
            {'$sample': {'size': sample_size}}
        ]
        
        

        foundLogin = mongo['users'].find_one({ "username": random_user })

        foundLoginId = foundLogin.get('_id')
        
        
        for card in random_cards:
            card_id = card.get('_id')
            foundDeck = mongo['decks'].find_one({ "name": deck_name, "user_id": foundLoginId })
            if foundDeck == None:
                mongo['decks'].insert_one({"name": deck_name, "cards_id": [card_id], "user_id": foundLoginId})
            else:
                mongo['decks'].update_one({'name': deck_name, "user_id": foundLoginId}, {'$push': { 'cards_id': {'$each': [card_id]}}})

        
        
    for document in mongo["decks"].find():
        id = str(document.get('_id'))
        name = document.get('name')
        user_id = str(document.get('user_id'))
        cards_id = document.get('cards_id')
        
        create_deck(id=id, name=name)
        create_user_deck_relationship(user_id=user_id, deck_id=id)

        for card_id in cards_id:
            create_deck_card_relationship(deck_id=id, card_id=card_id)
