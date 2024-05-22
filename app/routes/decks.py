from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel
from db.mongo import MongoManager
from pymongo import MongoClient
from typing import Annotated
from app.routes.auth import get_current_user, User
from PIL import Image
import io

# from pymongo import MongoClient

class Deck(BaseModel):
    cardName: str
    deckName: str
		
router = APIRouter()

mongo = MongoManager.get_instance()

cards = mongo["cards"]
decks = mongo["decks"]

@router.post("/create/")
async def create(deck: Deck, current_user: Annotated[User, Depends(get_current_user)]):
    duplicate = False

    foundCard = cards.find_one({ "name": deck.cardName })

    foundDeck = decks.find_one({ "name": deck.deckName, "user_id": current_user.id })

    if foundCard != None:

        foundCardId = foundCard.get('_id')

        if foundDeck == None:
            decks.insert_one({"name": deck.deckName, "cards_id": [foundCardId], "user_id": current_user.id})
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
                result = decks.update_one({'name': deck.deckName, "user_id": current_user.id}, {'$push': { 'cards_id': {'$each': [foundCardId]}}})
                return {"message": "Dodano kartę do talii. Obecna ilość kart w talii wynosi: " + str(len(foundDeck['cards_id']) + 1)}
    else:
        return {"message": "Podana nazwa karty jest nieprawidłowa"}
        
        
@router.delete("/deck/{id}/")
async def delete_deck(id: str):
    #nie działa
    found_deck = decks.find_one({ "_id": id })

    if found_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")

    decks.delete_one({ "_id": id })

    return {"message": "Deck has been deleted"}

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