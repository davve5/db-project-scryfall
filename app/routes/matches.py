from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from db.mongo import MongoManager

class Match(BaseModel):
    winners_deck: str
    loeser_deck: str
    winners_cards: str
    looser_cards: str
    winner_player: str
    looser_player: str
		
router = APIRouter()

mongo = MongoManager.get_instance()


# @router.get("/", response_class=List[Match])
# async def create_user_matches():
# 	# cursor = mongo['matches'].find({ "user_id": user_id })
# 	# return list(cursor)
# 	return []


@router.get("/{match_id}", response_class=Match)
async def create_user_matches(match_id: str):
	# match = mongo['matches'].find_one({ "_id": match_id, "user_id": user_id })
	return Match(**match)


@router.delete("/{match_id}")
async def create_user_matches(match_id: str):
	# cursor = mongo['matches'].find({ "_id": match_id, "user_id": user_id })
	return list(cursor)


@router.post("/create")
async def create_match(match: Match):
    return "hello games"
