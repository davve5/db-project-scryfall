import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from app.routes.matches import create_match_lost_won_relationship
import random

def insert():
    mongo = MongoManager.get_instance()
    neo4j = Neo4jManager.get_instance()

    decks = mongo["decks"].find()
    decks = list(map(lambda x: x.get('_id'), decks))

    for i in range(len(decks) * 2):
        winner = random.choice(decks)
        looser = random.choice(decks)
        create_match_lost_won_relationship(winner_deck_id=winner, looser_deck_id=looser)