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
    object: str
    id: ObjectId = Field(alias="_id")
    multiverse_ids: List[int]
    mtgo_id: Optional[int] = None
    mtgo_foil_id: Optional[int] = None
    tcgplayer_id: Optional[int] = None
    cardmarket_id: Optional[int] = None
    name: str
    lang: str
    released_at: str
    uri: str
    scryfall_uri: str
    layout: str
    highres_image: bool
    image_status: str
    image_uris: Optional[ImageUris] = None
    mana_cost: Optional[str] = None
    cmc: Optional[float] = None
    type_line: Optional[str] = None
    power: Optional[str] = None
    toughness: Optional[str] = None
    colors: List[str] = []
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
    flavor_text: Optional[str] = None
    card_back_id: Optional[str] = None
    artist: str
    artist_ids: List[str] = []
    illustration_id: Optional[str] = None
    border_color: str
    frame: str
    full_art: bool
    textless: bool
    booster: bool
    story_spotlight: bool
    edhrec_rank: Optional[int] = None
    penny_rank: Optional[int] = None
    prices: Prices
    purchase_uris: Optional[PurchaseUris] = None


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
        query["rarity"] = rarity.lower()
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
    id: str
    name: str
    counter: int


class SynergyCard(BaseModel):
    name: str
    id: str
    synergy: int

@router.get("/recommended/{card_id}", response_model=List[PopularCard])
def get_popular_cards(card_id: str):
    neo4j = Neo4jManager.get_instance()
    type_line = ""
    
    type_line = mongo['cards'].find_one({ "_id": ObjectId(card_id)}).get('type_line') or ""

    if len(type_line) > 0:
        type_line = type_line.split()[0]

    cards = neo4j.run(
        """
            MATCH (selected_card:Card {id: $card_id})<-[:CONTAINS]-(deck:Deck)-[:CONTAINS]->(other_card:Card)
            WHERE other_card <> selected_card AND other_card.type_line CONTAINS $type_line
            WITH other_card, COUNT(other_card) AS popularity
            ORDER BY popularity DESC
            LIMIT 5
            RETURN other_card.name AS name, other_card.id AS id, other_card.type_line AS type_line, popularity
        """,
        {"card_id": card_id, "type_line": type_line}
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


    return {"message": "The given card has a victory factor of: " + str(win_percent) + "% at " + str(win_count) + " won matches and " + str(lose_count) + " matches lost."}


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


@router.get("/card_synergy/{card_id}", response_model=List[SynergyCard])
def get_card_synergy(card_id: str):
    neo4j = Neo4jManager.get_instance()
    result = neo4j.run(
        """
            MATCH (selected_card:Card {id: $card_id})<-[:CONTAINS]-(d:Deck)-[:CONTAINS]->(other_card:Card)
            WHERE other_card <> selected_card
            OPTIONAL MATCH (d)-[:WON_AGAINST]->(opponent)
            WITH other_card, d, COUNT(opponent) AS synergy
            ORDER BY synergy DESC
            LIMIT 5
            RETURN other_card.name AS name, other_card.id AS id, synergy
        """,
        {"card_id": card_id}
    )


    return result
