from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from db.mongo import MongoManager

# from pymongo import MongoClient

class Deck(BaseModel):
    name: str
    cards: []
		
router = APIRouter()

cards = db["cards"]
decks = db["decks"]
mongo = MongoManager.get_instance()

@router.post("/create/")
async def create(decks: Deck):
    duplicate = False
    cardName = input()

    foundCard = cards.find_one({ "name": cardName })

    foundDeck = decks.find_one({ "name": deckName, "userId": 1 })

    if foundCard != None:

        foundCardId = foundCard.get('_id')

        if foundDeck == None:
            decks.insert_one({"name": deckName, "cardsId": [foundCardId], "userId": 1})

        else:
            for card in foundDeck['cardsId']:
                if card == foundCardId:
                    duplicate = True
            if duplicate:
                    print("Podana karta jest już w talii")
            else:
                result = decks.update_one({'name': deckName, "userId": 1}, {'$push': { 'cardsId': {'$each': [foundCardId]}}})
                print("Dodano kartę do talii")
                print("Obecna ilość kart w talii wynosi:", len(foundDeck['cardsId']) + 1)
    else:
        print("Podana nazwa karty jest nieprawidłowa")
        continue

