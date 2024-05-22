from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel
from db.mongo import MongoManager
from pymongo import MongoClient
from typing import Annotated
from app.routes.auth import get_current_user, User
from PIL import Image
import io
from bson.objectid import ObjectId
from db.neo4j import Neo4jManager

class Collection(BaseModel):
    cardName: str
		
router = APIRouter()

mongo = MongoManager.get_instance()

cards = mongo["cards"]
cards_collection = mongo["cards_collection"]

def create_user_card_relationship(user_id: str, card_id: str):
    neo4j = Neo4jManager.get_instance()
    params = { "user_id": str(user_id), "card_id": str(card_id) }
    neo4j.run(
        "MATCH (u:User {id: $user_id}), (c:Card {id: $card_id}) CREATE (u)-[:HAS_CARD]->(c)",
        params
    )
    neo4j.run(
        "MATCH (c:Card {id: $card_id}), (u:User {id: $user_id}) CREATE (c)-[:BELONGS_TO]->(u)",
        params
    )

    
@router.post("/create/")
async def create(collection: Collection, current_user: Annotated[User, Depends(get_current_user)]):
    duplicate = False

    foundCard = cards.find_one({ "name": collection.cardName })

    foundCollection = cards_collection.find_one({ "user_id": current_user.id })

    if foundCard != None:

        foundCardId = foundCard.get('_id')
        # FIXME: Propably upsert? To be checked
        if foundCollection == None:
            cards_collection.insert_one({ "user_id": current_user.id, "cards_id": [foundCardId] })
            create_user_card_relationship(user_id=current_user.id, card_id=foundCardId)

            return {"message": "Utworzono kolekcję i dodano kartę"}

        else:
            for card in foundCollection['cards_id']:
                if card == foundCardId:
                    duplicate = True
            if duplicate:
                    return {"message": "Podana karta jest już w kolekcji"}
            else:
                result = cards_collection.update_one({ "user_id": current_user.id}, {'$push': { 'cards_id': {'$each': [foundCardId]}}})
                create_user_card_relationship(user_id=current_user.id, card_id=foundCardId)
                return {"message": "Dodano kartę do kolekcji. Obecna ilość kart w kolekcji wynosi: " + str(len(foundCollection['cards_id']) + 1)}
    else:
        return {"message": "Podana nazwa karty jest nieprawidłowa"}
        
        
@router.get("/show/")
async def show(current_user: Annotated[User, Depends(get_current_user)]):

    userCollection = cards_collection.find_one({"user_id": current_user.id})

    for card in userCollection["cards_id"]:
        foundCard = cards.find_one({ "_id": card })
        image_binary = foundCard["binary_image"]
        image = Image.open(io.BytesIO(image_binary))
    
        image.show()
    
    return {"message": "Wyświetlam zdjęcia kolekcji użytkownika"}
    

@router.get('/count/{card_id}')
async def count(card_id: str):
    result = cards_collection.aggregate([
        {
            "$match": { "cards_id": ObjectId(card_id) },
        },
        {
             "$group": { "_id": "$user_id" }
        },
        {
            "$count": "user_count"
        }
    ]).next()


    return {"count": result.get('user_count')}