from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from db.mongo import MongoManager
from typing import Annotated, List
from app.routes.auth import get_current_user, User
from bson.objectid import ObjectId
from db.neo4j import Neo4jManager
from app.routes.cards_collection import create_user_card_relationship
BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}

class Match(BaseModel):
    my_deck_id: str
    enemy_id: str
    enemy_deck_id: str
    result: int

router = APIRouter()

class MetchResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: ObjectId = Field(alias="_id")
    winner_id: ObjectId = Field()
    loser_id: ObjectId = Field()
    winner_deck_id: ObjectId = Field()
    looser_deck_id: ObjectId = Field()

def delete_match_lost_won_relationship(winner_deck_id: str, looser_deck_id:str):
    neo4j = Neo4jManager.get_instance()
    params = { "winner_deck_id": str(winner_deck_id), "looser_deck_id": str(looser_deck_id) }
    neo4j.run(

        "MATCH (winner:Deck {id: $winner_deck_id})-[r:WON_AGAINST]->(looser:Deck {id: $looser_deck_id}) DELETE r",
        params
    )
    neo4j.run(
        "MATCH (looser:Deck {id: $looser_deck_id})-[r:LOST_AGAINST]->(winner:Deck {id: $winner_deck_id}) DELETE r",
        params
    )
    
    
def create_match_lost_won_relationship(winner_deck_id: str, looser_deck_id:str):
    neo4j = Neo4jManager.get_instance()
    params = { "winner_deck_id": str(winner_deck_id), "looser_deck_id": str(looser_deck_id) }
    neo4j.run(
        "MATCH (winner:Deck {id: $winner_deck_id}), (looser:Deck {id: $looser_deck_id}) CREATE (winner)-[:WON_AGAINST]->(looser)",
        params
    )
    neo4j.run(
        "MATCH (winner:Deck {id: $winner_deck_id}), (looser:Deck {id: $looser_deck_id}) CREATE (looser)-[:LOST_AGAINST]->(winner)",
        params
    )


@router.post("/")
async def create(match: Match, current_user: Annotated[User, Depends(get_current_user)]):
    mongo = MongoManager.get_instance()
    enemy = mongo['users'].find_one({"_id": ObjectId(match.enemy_id)})

    winner_id = current_user.id
    loser_id = enemy.get('_id')

    if match.result < 1:
        winner_id, loser_id = loser_id, winner_id

    winner_deck = mongo['decks'].find_one({ "_id": ObjectId(match.my_deck_id) })
    looser_deck = mongo['decks'].find_one({ "_id": ObjectId(match.enemy_deck_id) })

    match = mongo['matches'].insert_one({
        "winner_id": winner_id,
        "loser_id": loser_id,
        "winner_deck_id": winner_deck.get('_id'),
        "looser_deck_id": looser_deck.get('_id'),
    })

    create_match_lost_won_relationship(winner_deck_id=winner_deck.get('_id'), looser_deck_id=looser_deck.get('_id'))

    return {"message": "Match created successfully", id: match.inserted_id}

@router.get("/{match_id}")
async def find_one(match_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    mongo = MongoManager.get_instance()
    match = mongo['matches'].find_one({ "_id": ObjectId(match_id), "$or": [
            { "winner_id": ObjectId(current_user.id) },
            { "loser_id": ObjectId(current_user.id) }
        ]})

    return MetchResult(**match)
    
    
@router.delete("/{match_id}")
async def delete(match_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    mongo = MongoManager.get_instance()
    match = mongo['matches'].find_one(
        { "_id": ObjectId(match_id),
        "$or": [
            { "winner_id": ObjectId(current_user.id) },
            { "loser_id": ObjectId(current_user.id) }
        ]}
        )
    mongo['matches'].delete_one({ "_id": ObjectId(match_id),
        "$or": [
            { "winner_id": ObjectId(current_user.id) },
            { "loser_id": ObjectId(current_user.id) }
        ]})

    delete_match_lost_won_relationship(winner_deck_id=match.get('winner_deck_id'), looser_deck_id=match.get('looser_deck_id'))
    return {"message": "Match deleted"}