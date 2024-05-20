from typing import List, Optional, Dict, Any
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from db.mongo import MongoManager
from bson.objectid import ObjectId
import re

BaseModel.model_config["json_encoders"] = {ObjectId: lambda v: str(v)}

router = APIRouter()


class ImageUris(BaseModel):
    small: str
    normal: str
    large: str
    png: str
    art_crop: str
    border_crop: str


class Legalities(BaseModel):
    standard: str
    future: str
    historic: str
    timeless: str
    gladiator: str
    pioneer: str
    explorer: str
    modern: str
    legacy: str
    pauper: str
    vintage: str
    penny: str
    commander: str
    oathbreaker: str
    standardbrawl: str
    brawl: str
    alchemy: str
    paupercommander: str
    duel: str
    oldschool: str
    premodern: str
    predh: str


class Prices(BaseModel):
    usd: Optional[str]
    usd_foil: Optional[str]
    usd_etched: Any
    eur: Optional[str]
    eur_foil: Optional[str]
    tix: Optional[str]


class PurchaseUris(BaseModel):
    tcgplayer: Optional[HttpUrl]
    cardmarket: Optional[HttpUrl]
    cardhoarder: Optional[HttpUrl]


class Card(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # FIXME: int | ObjectId = Field(alias="_id")
    object: str
    id: ObjectId = Field(alias="_id")
    multiverse_ids: List[int]
    mtgo_id: int | ObjectId = Field(alias="_id")
    mtgo_foil_id: int | ObjectId = Field(alias="_id")
    tcgplayer_id: int | ObjectId = Field(alias="_id")
    cardmarket_id: int | ObjectId = Field(alias="_id")
    name: str
    lang: str
    released_at: str
    uri: str
    scryfall_uri: str
    layout: str
    highres_image: bool
    image_status: str
    image_uris: ImageUris | ObjectId = Field(alias="_id")
    mana_cost: str | ObjectId = Field(alias="_id")
    cmc: float | ObjectId = Field(alias="_id")
    type_line: str | ObjectId = Field(alias="_id")
    power: str | ObjectId = Field(alias="_id")
    toughness: str | ObjectId = Field(alias="_id")
    colors: List[str] | ObjectId = Field(alias="_id")
    color_identity: List[str]
    keywords: List
    legalities: Legalities
    games: List[str]
    reserved: bool
    foil: bool
    nonfoil: bool
    finishes: List[str]
    oversized: bool
    promo: bool
    reprint: bool
    variation: bool
    set_id: str
    set: str
    set_name: str
    set_type: str
    set_uri: str
    set_search_uri: str
    scryfall_set_uri: str
    rulings_uri: str
    prints_search_uri: str
    collector_number: str
    digital: bool
    rarity: str
    flavor_text: str | ObjectId = Field(alias="_id")
    card_back_id: str | ObjectId = Field(alias="_id")
    artist: str
    artist_ids: List[str] | ObjectId = Field(alias="_id")
    illustration_id: str | ObjectId = Field(alias="_id")
    border_color: str
    frame: str
    full_art: bool
    textless: bool
    booster: bool
    story_spotlight: bool
    edhrec_rank: int | ObjectId = Field(alias="_id")
    penny_rank: int | ObjectId = Field(alias="_id")
    prices: Prices
    purchase_uris: PurchaseUris | ObjectId = Field(alias="_id")


mongo = MongoManager.get_instance()

@router.get("/search/", response_model=list[Card])
async def search(
    name: Optional[str] = None,
    color_identity: Optional[str] = None,
    rarity: Optional[str] = None,
    type_line: Optional[str] = None,
    legalities: Optional[str] = None,
    set_type: Optional[str] = None,
    power: Optional[str] = None,
    toughness: Optional[str] = None,
    mana_cost: Optional[str] = None
) :

    query = {}
    if name is not None:
        query["name"] = {"$regex": re.compile(name, re.IGNORECASE)}
    if color_identity is not None:
        query["color_identity"] = color_identity.capitalize()
    if rarity is not None:
        query["rarity"] = rarity
    if type_line is not None:
        query["type_line"] = type_line
    if legalities is not None:
        query[f"legalities.{legalities}"] = "legal"
    if set_type is not None:
        query["set_type"] = {"$regex": re.compile(name, re.IGNORECASE)}
    if power is not None:
        query["power"] = power
    if toughness is not None:
        query["toughness"] = toughness
    if mana_cost is not None:
        query["mana_cost"] = mana_cost

    cursor = mongo['cards'].find(query).limit(20)

    return cursor
