from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from db.mongo import MongoManager

# from pymongo import MongoClient

class Game(BaseModel):
    winners_deck: str
    loeser_deck: str
    winners_cards: str
    looser_cards: str
    winner_player: str
    looser_player: str
		
router = APIRouter()

mongo = MongoManager.get_instance()

@router.post("/create/")
async def create_game(game: Game):
    return "hello games"
