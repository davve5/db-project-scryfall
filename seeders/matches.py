import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from app.routes.matches import create_match_lost_won_relationship
import random

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()
    random.seed(1234)
    decks = mongo["decks"].find()
    decks = list(decks)

    for i in range(len(decks) * 5):
        winner = random.choice(decks)
        looser = random.choice(decks)

        match = mongo['matches'].insert_one({
            "winner_id": winner.get('user_id'),
            "loser_id": looser.get('user_id'),
            "winner_deck_id": winner.get('_id'),
            "looser_deck_id": looser.get('_id'),
        })

        create_match_lost_won_relationship(winner_deck_id=winner.get('_id'), looser_deck_id=looser.get('_id'))