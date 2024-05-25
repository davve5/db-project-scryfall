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
		
        
class OwnedByCard(BaseModel):
    id: str
    name: str
    owned_by: int
    all_users: int


router = APIRouter()

mongo = MongoManager.get_instance()

cards = mongo["cards"]
cards_collection = mongo["cards_collection"]

def create_user_card_relationship(user_id: str, card_id: str):
    neo4j = Neo4jManager.get_instance()
    params = { "user_id": str(user_id), "card_id": str(card_id) }
    neo4j.run(
        "MATCH (u:User {id: $user_id}), (c:Card {id: $card_id}) CREATE (u)-[:HAS]->(c)",
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

            return {"message": "Collection created and card added"}

        else:
            for card in foundCollection['cards_id']:
                if card == foundCardId:
                    duplicate = True
            if duplicate:
                    return {"message": "Card already in collection"}
            else:
                result = cards_collection.update_one({ "user_id": current_user.id}, {'$push': { 'cards_id': {'$each': [foundCardId]}}})
                create_user_card_relationship(user_id=current_user.id, card_id=foundCardId)
                return {"message": "Card added. Cards counter: " + str(len(foundCollection['cards_id']) + 1)}
    else:
        return {"message": "Card not found"}
        
        
@router.get("/show/")
async def show(current_user: Annotated[User, Depends(get_current_user)]):

    userCollection = cards_collection.find_one({"user_id": current_user.id})

    for card in userCollection["cards_id"]:
        foundCard = cards.find_one({ "_id": card })
        image_binary = foundCard["binary_image"]
        image = Image.open(io.BytesIO(image_binary))
    
        image.show()
    
    return {"message": "Showing card collection images"}
    

@router.get('/{card_id}/count')
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
    
    
    
@router.delete("/card/{cardid}")
async def delete_card(cardid, current_user: Annotated[User, Depends(get_current_user)]):

    user_id = ObjectId(current_user.id)

    card_id = ObjectId(cardid)

    cards_collection.update_one({ "user_id": user_id }, { "$pull": { "cards_id": card_id } })

    neo4j = Neo4jManager.get_instance()
    params = { "user_id": str(user_id), "card_id": str(card_id) }

    neo4j.run(
        "MATCH (c:Card {id: $card_id})-[r:BELONGS_TO]->(u:User {id: $user_id}) DELETE r",
        params
    )

    neo4j.run(
        "MATCH (u:User {id: $user_id})-[r:HAS]->(c:Card {id: $card_id}) DELETE r",
        params
    )

    return {"message": "Card has been deleted"}
    
    
@router.get("/owned_by/{card_id}")
def get_owned_cards(card_id: str):
    neo4j = Neo4jManager.get_instance()

    cards = neo4j.run(
        """
            MATCH (c:Card {id: $card_id})-[:BELONGS_TO]->(u:User)
            WITH c, COUNT(u) AS owned_by
            MATCH (n:User)
            WITH c, owned_by, COUNT(n) AS all_users
            RETURN c.id AS id, c.name AS name, owned_by, all_users
        """,
        {"card_id": card_id}
    )
    
    result = cards.single()

    return {"message": "The card " + result['name'] + "is owned by: " + str((result['owned_by'] / result['all_users']) * 100) + "% of users."}