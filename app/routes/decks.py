from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from db.mongo import MongoManager
from pymongo import MongoClient

# from pymongo import MongoClient

class Deck(BaseModel):
    cardName: str
    deckName: str
    userId: int
		
router = APIRouter()

mongo = MongoManager.get_instance()

cards = mongo["cards"]
decks = mongo["decks"]

@router.post("/create/")
async def create(deck: Deck):
    duplicate = False

    foundCard = cards.find_one({ "name": deck.cardName })

    foundDeck = decks.find_one({ "name": deck.deckName, "userId": 1 })

    if foundCard != None:

        foundCardId = foundCard.get('_id')

        if foundDeck == None:
            decks.insert_one({"name": deck.deckName, "cardsId": [foundCardId], "userId": 1})

        else:
            for card in foundDeck['cardsId']:
                if card == foundCardId:
                    duplicate = True
            if duplicate:
                    return {"message": "Podana karta jest już w talii"}
            else:
                result = decks.update_one({'name': deck.deckName, "userId": 1}, {'$push': { 'cardsId': {'$each': [foundCardId]}}})
                return {"message": "Dodano kartę do talii. Obecna ilość kart w talii wynosi: " + str(len(foundDeck['cardsId']) + 1)}
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
    decks.update_one({ "_id": deck_id }, { "$pull": { "decks.cardsId": card_id } })

    
    return {"message": "Karta została usunięta"}
