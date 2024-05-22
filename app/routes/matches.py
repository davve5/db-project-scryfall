from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel
from db.mongo import MongoManager
from typing import Annotated
from app.routes.auth import get_current_user, User
from bson.objectid import ObjectId

class Match(BaseModel):
    enemy_id: str
    my_deck_id: str
    enemy_deck_id: str
    result: int
		
router = APIRouter()

mongo = MongoManager.get_instance()


@router.post("/")
async def create_match(match: Match, current_user: Annotated[User, Depends(get_current_user)]):
    enemy = mongo['users'].find_one({"_id": ObjectId(match.enemy_id)})
    
    winner_id = current_user.id
    loser_id = enemy.get('_id')

    if match.result < 1:
        winner_id, loser_id = loser_id, winner_id

    winner_deck = mongo['decks'].find_one({ "_id": ObjectId(match.my_deck_id) })
    looser_deck = mongo['decks'].find_one({ "_id": ObjectId(match.enemy_deck_id) })
    
    result = mongo['matches'].insert_one({
        "winner_id": winner_id,
        "loser_id": loser_id,
        "winner_deck_id": winner_deck.get('_id'),
        "looser_deck_id": looser_deck.get('_id'),
        "winner_deck": winner_deck.get('cards_id'),
        "looser_deck": looser_deck.get('cards_id'),
    })

    return {"message": "Match created successfully"}

@router.get("/{match_id}", response_class=Match)
async def create_user_matches(match_id: str):
	# match = mongo['matches'].find_one({ "_id": match_id, "user_id": user_id })
	return Match(**match)


@router.delete("/{match_id}")
async def create_user_matches(match_id: str):
	# cursor = mongo['matches'].find({ "_id": match_id, "user_id": user_id })
	return list(cursor)
