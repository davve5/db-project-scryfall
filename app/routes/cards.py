from typing import List, Optional, Dict, Any
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from db.mongo import MongoManager
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder

BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}

router = APIRouter()

class Card(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # FIXME: Get card id
    _id: ObjectId
    object: Optional[str]
    oracle_id: Optional[str]
    name: Optional[str]
    mana_cost: Optional[str]
    type_line: Optional[str]
    power: Optional[str]
    toughness: Optional[str]
    colors: Optional[List[str]]
    rarity: Optional[str]

mongo = MongoManager.get_instance()

@router.get("/search/", response_model=list[Card])
async def search(
    name: Optional[str] = None,
    color: Optional[str] = None,
    rarity: Optional[str] = None,
    type_line: Optional[str] = None,
    legal: Optional[str] = None,
    set_name: Optional[str] = None,
    power: Optional[str] = None,
    toughness: Optional[str] = None,
    cost: Optional[str] = None
) :
    query = {}
    if name is not None:
        query["name"] = name
    if color is not None:
        query["color"] = color
    if rarity is not None:
        query["rarity"] = rarity
    if type_line is not None:
        query["type_line"] = type_line
    if legal is not None:
        query["legal"] = legal
    if set_name is not None:
        query["set_name"] = set_name
    if power is not None:
        query["power"] = power
    if toughness is not None:
        query["toughness"] = toughness
    if cost is not None:
        query[""] = cost

    cursor = mongo['cards'].find(query)

    return cursor
