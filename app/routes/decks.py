from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel
from db.mongo import MongoManager
from pymongo import MongoClient
from typing import Annotated
from app.routes.auth import get_current_user, User
from PIL import Image
import io
from app.routes.cards_collection import create_user_card_relationship
from db.neo4j import Neo4jManager
from bson.objectid import ObjectId
# from pymongo import MongoClient

class Deck(BaseModel):
    cardName: str
    deckName: str
		
router = APIRouter()

mongo = MongoManager.get_instance()

cards = mongo["cards"]
decks = mongo["decks"]


def create_user_deck_relationship(user_id: str, deck_id: str):
    neo4j = Neo4jManager.get_instance()
    params = { "user_id": str(user_id), "deck_id": str(deck_id) }
    neo4j.run(
        "MATCH (u:User {id: $user_id}), (d:Deck {id: $deck_id}) CREATE (u)-[:HAS]->(d)",
        params
    )
    neo4j.run(
        "MATCH (d:Deck {id: $deck_id}), (u:User {id: $user_id}) CREATE (d)-[:BELONGS_TO]->(u)",
        params
    )

def create_deck(id: str, name: str):
    neo4j = Neo4jManager.get_instance()
    neo4j.run(
        "CREATE (d:Deck {id: $id, name: $name})",
        {"id": str(id), "name": name}
    )


def create_deck_card_relationship(deck_id: str, card_id: str):
    neo4j = Neo4jManager.get_instance()
    params = { "deck_id": str(deck_id), "card_id": str(card_id) }
    neo4j.run(
        "MATCH (c:Card {id: $card_id}), (d:Deck {id: $deck_id}) CREATE (c)-[:BELONGS_TO]->(d)",
        params
    )
    neo4j.run(
        "MATCH (d:Deck {id: $deck_id}), (c:Card {id: $card_id}) CREATE (d)-[:CONTAINS]->(c)",
        params
    )


#FIXME: Create do tworzenia update do updateowania
# To powinny byc 2 metody
@router.post("/create/")
async def create(deck: Deck, current_user: Annotated[User, Depends(get_current_user)]):
    card = cards.find_one({ "name": deck.cardName })
    deck = decks.find_one({ "name": deck.deckName, "user_id": current_user.id })

    if foundCard != None:

        foundCardId = foundCard.get("_id")
        # Pierwszy route /create
        if foundDeck == None:
            # FIXME: Propably upsert? To be checked
            result = decks.insert_one({"name": deck.deckName, "cards_id": [foundCardId], "user_id": current_user.id})
            create_deck(id=result.inserted_id, name=deck.deckName)
            create_user_deck_relationship(user_id=current_user.id, deck_id=result.inserted_id)
            create_deck_card_relationship(deck_id=result.inserted_id, card_id=foundCardId)

            return {"message": "New deck created. Added card"}
        elif len(foundDeck['cards_id']) >= 40:
            return {"message": "Deck limit reached"}
        else:
            for card in foundDeck["cards_id"]:
                if card == foundCardId:
                    duplicate = True
            if duplicate:
                    return {"message": "Card already in deck"}
            else:
                # Drugi route /update

                result = decks.update_one({'name': deck.deckName, "user_id": current_user.id}, {'$push': { 'cards_id': {'$each': [foundCardId]}}})
                deck = decks.find_one({'name': deck.deckName, "user_id": current_user.id})
                create_user_deck_relationship(user_id=current_user.id, deck_id=deck.get('_id'))
                create_deck_card_relationship(deck_id=deck.get('_id'), card_id=foundCardId)
                return {"message": "Card added. Cards currently in deck: " + str(len(foundDeck['cards_id']) + 1)}

    else:
        return {"message": "Card name not found"}
        
        

@router.delete("/deck/{id}/")
async def delete_deck(id):

    # FIXME: ObjectId(id)
    # Nie musisz sprawdzac czy istnieje przed usunieciem, uwuanie rzuca wyjatek to wystarczy
    deck_id = ObjectId(id)
    found_deck = decks.find_one({ "_id": deck_id })

    if found_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")

    decks.delete_one({ "_id": deck_id })
    
    neo4j = Neo4jManager.get_instance()
    params = { "deck_id": str(deck_id) }

    neo4j.run(
        "MATCH (d:Deck {id: $deck_id}) DETACH DELETE d",
        params
)

    return {"message": "Deck has been deleted"}

# FIXME: Niepotrzebne $ w nazwie route'a
@router.delete("/deck/{deckid}/card/{cardid}")
async def delete_card(deckid, cardid):

    deck_id = ObjectId(deckid)
    
    card_id = ObjectId(cardid)
    
    decks.update_one({ "_id": deck_id }, { "$pull": { "cards_id": card_id } })

    neo4j = Neo4jManager.get_instance()
    params = { "deck_id": str(deck_id), "card_id": str(card_id) }

    neo4j.run(
        "MATCH (c:Card {id: $card_id})-[r:BELONGS_TO]->(d:Deck {id: $deck_id}) DELETE r",
        params
    )

    neo4j.run(
        "MATCH (d:Deck {id: $deck_id})-[r:CONTAINS]->(c:Card {id: $card_id}) DELETE r",
        params
    )
    
    return {"message": "Card has been deleted"}


@router.get("/show/")
async def show(deck: Deck, current_user: Annotated[User, Depends(get_current_user)]):
    foundDeck = decks.find_one({ "name": deck.deckName, "user_id": current_user.id })

    for card in foundDeck["cards_id"]:
        foundCard = cards.find_one({ "_id": card })
        image_binary = foundCard["binary_image"]
        image = Image.open(io.BytesIO(image_binary))
    
        image.show()
    
    return { "message": "Showing deck images " + deck.deckName }

class WinningPropability(BaseModel):
    id: str
    name: str
    win_rate: float

@router.get("/{deck_id}/winning", response_model=WinningPropability)
async def winning_propability(deck_id: str):
    neo4j = Neo4jManager.get_instance()
    result = neo4j.run(
        """
            MATCH (d:Deck {id: $deck_id})
            OPTIONAL MATCH (d)-[:WON_AGAINST]->(opponent)
            WITH d, COUNT(opponent) AS wins
            OPTIONAL MATCH (d)-[:WON_AGAINST|LOST_AGAINST]->(games)
            WITH d, wins, COUNT(games) AS total_games
            RETURN d.name AS name, d.id AS id,
                CASE
                    WHEN total_games > 0 THEN toFloat(wins) / toFloat(total_games) 
                    ELSE 0
                END AS win_rate
        """,
        {"deck_id": deck_id}
    )

    return result.single()
