from typing import List, Optional, Dict, Any
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from db.mongo import MongoManager
from bson.objectid import ObjectId
import re
from db.neo4j import Neo4jManager

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
async def search_cards(
    name: Optional[str] = None,
    color_identity: Optional[str] = None,
    rarity: Optional[str] = None,
    type_line: Optional[str] = None,
    legalities: Optional[str] = None,
    set_type: Optional[str] = None,
    power: Optional[str] = None,
    toughness: Optional[str] = None,
    mana_cost: Optional[str] = None
):

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

class PopularCard(BaseModel):
    name: str
    id: str
    popularity: int

class CounterCard(BaseModel):
    name: str
    id: str
    counter: int

#TODO: change to recommended
@router.get("/popular/{card_id}", response_model=List[PopularCard])
def get_popular_cards(card_id: str):
    neo4j = Neo4jManager.get_instance()
    cards = neo4j.run(
        """
            MATCH (selected_card:Card {id: $card_id})<-[:CONTAINS]-(deck:Deck)-[:CONTAINS]->(other_card:Card)
            WHERE other_card <> selected_card
            WITH other_card, COUNT(other_card) AS popularity
            ORDER BY popularity DESC
            LIMIT 5
            RETURN other_card.name AS name, other_card.id AS id, popularity
        """,
        {"card_id": card_id}
    )

    return cards


@router.get("/win_probability/{card_id}")
def get_card_win_probability(card_id: str):
    neo4j = Neo4jManager.get_instance()
    result = neo4j.run(
        """
            MATCH (d:Deck)-[:CONTAINS]->(c:Card {id: $card_id})
            OPTIONAL MATCH (d)-[:WON_AGAINST]->(opponent:Deck)
            WITH d, c, COUNT(opponent) AS wins
            OPTIONAL MATCH (d)-[:LOST_AGAINST]->(opponent:Deck)
            WITH c, wins, COUNT(opponent) AS losses
            RETURN 
               wins, 
               losses
        """,
        {"card_id": card_id}
    )
    
    win_count = 0
    lose_count = 0
    win_percent = 0
    
    for r in result:
        win_count = win_count + r['wins']
        lose_count = lose_count + r['losses']
        
    if win_count > 0:
        if lose_count > 0:
            win_percent = win_count / (win_count + lose_count)
        else:
            win_percent = 1
    
    win_percent = win_percent * 100
    
        
    return {"message": "Podana karta ma współczynnik zwycięstwa równy: " + str(win_percent) + "% na " + str(win_count) + " wygrane mecze i " + str(lose_count) + " przegranych meczy."}


@router.get("/card_counter/{card_id}", response_model=List[CounterCard])
def get_card_counter(card_id: str):
    neo4j = Neo4jManager.get_instance()
    result = neo4j.run(
        """
            MATCH (d:Deck)-[:CONTAINS]->(c:Card {id: $card_id})
            OPTIONAL MATCH (d)-[:LOST_AGAINST]->(opponent:Deck)
            OPTIONAL MATCH (opponent)-[:CONTAINS]->(opponent_card:Card)
            WITH opponent_card
            RETURN opponent_card.name AS name, opponent_card.id AS id, COUNT(opponent_card) AS counter
            ORDER BY counter DESC
            LIMIT 5
        """,
        {"card_id": card_id}
    )
    
        
    return result