from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from db.mongo import MongoManager

# from pymongo import MongoClient

class Credentials(BaseModel):
    login: str
    password: str
		
router = APIRouter()

mongo = MongoManager.get_instance()

@router.get("/search/")
async def search(
    name: str | None = None,
    color: str | None = None,
    rarity: str | None = None,
    type_line: str | None = None,
    legal: str | None = None,
    set_name: str | None = None,
    power: str | None = None,
    toughness: str | None = None,
    cost: str | None = None
):
    cards = mongo['cards'].find({
        "name": name,
        "color": color,
        "rarity": rarity,
        "type_line": type_line,
        "legal": legal,
        "set_name": set_name,
        "power": power,
        "toughness": toughness,
        "cost": cost
    })
    return {"hello": "world"}
