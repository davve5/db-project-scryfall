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
        "MATCH (u:User {id: $user_id}), (d:Deck {id: $deck_id}) CREATE (u)-[:HAS_DECK]->(d)",
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
        "MATCH (d:Deck {id: $deck_id}), (c:Card {id: $card_id}) CREATE (d)-[:HAS_CARD]->(c)",
        params
    )


#FIXME: Create do tworzenia update do updateowania
# To powinny byc 2 metody
@router.post("/create/")
async def create(deck: Deck, current_user: Annotated[User, Depends(get_current_user)]):
    duplicate = False

    foundCard = cards.find_one({ "name": deck.cardName })

    foundDeck = decks.find_one({ "name": deck.deckName, "user_id": current_user.id })

    if foundCard != None:

        foundCardId = foundCard.get('_id')
        # Pierwszy route /create
        if foundDeck == None:
            # FIXME: Propably upsert? To be checked
            result = decks.insert_one({"name": deck.deckName, "cards_id": [foundCardId], "user_id": current_user.id})
            create_deck(id=result.inserted_id, name=deck.deckName)
            create_user_deck_relationship(user_id=current_user.id, deck_id=result.inserted_id)
            create_deck_card_relationship(deck_id=result.inserted_id, card_id=foundCardId)
            return {"message": "Utworzono nową talię i dodano kartę"}
        elif len(foundDeck['cards_id']) >= 40:
            return {"message": "Osiągnięto limit kart w talii"}
        else:
            for card in foundDeck['cards_id']:
                if card == foundCardId:
                    duplicate = True
            if duplicate:
                    return {"message": "Podana karta jest już w talii"}
            else:
                # Drugi route /update
                result = decks.update_one({'name': deck.deckName, "user_id": current_user.id}, {'$push': { 'cards_id': {'$each': [foundCardId]}}})
                deck = decks.find_one({'name': deck.deckName, "user_id": current_user.id})
                create_user_deck_relationship(user_id=current_user.id, deck_id=deck.get('_id'))
                create_deck_card_relationship(deck_id=deck.get('_id'), card_id=foundCardId)
                return {"message": "Dodano kartę do talii. Obecna ilość kart w talii wynosi: " + str(len(foundDeck['cards_id']) + 1)}
    else:
        return {"message": "Podana nazwa karty jest nieprawidłowa"}
        
        
@router.delete("/deck/{id}/")
async def delete_deck(id: str):
    #nie działa

    # FIXME: ObjectId(id)
    # Nie musisz sprawdzac czy istnieje przed usunieciem, uwuanie rzuca wyjatek to wystarczy
    found_deck = decks.find_one({ "_id": id })

    if found_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")

    decks.delete_one({ "_id": id })

    return {"message": "Deck has been deleted"}

# FIXME: Niepotrzebne $ w nazwie route'a
@router.delete("/deck/${deck_id}/card/${card_id}")
async def delete_card(deck_id, card_id):
    #nie działa
    decks.update_one({ "_id": deck_id }, { "$pull": { "decks.cards_id": card_id } })

    
    return {"message": "Karta została usunięta"}


@router.get("/show/")
async def show(deck: Deck, current_user: Annotated[User, Depends(get_current_user)]):

    foundDeck = decks.find_one({ "name":deck.deckName, "user_id": current_user.id })

    for card in foundDeck["cards_id"]:
        foundCard = cards.find_one({ "_id": card })
        image_binary = foundCard["binary_image"]
        image = Image.open(io.BytesIO(image_binary))
    
        image.show()
    
    return { "message": "Wyświetlam zdjęcia talii " + deck.deckName }