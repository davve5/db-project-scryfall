from fastapi import FastAPI

from app.routes.main import api_router

from seeders import cards, users, decks, cards_collection, matches, images
from db.indexes import create_indexes

app = FastAPI()
create_indexes()

app.include_router(api_router)


@app.get("/seed")
async def root():
    users.insert()
    print("users inserted")
    cards.insert()
    print("cards inserted")
    cards_collection.insert()
    print("cards_collection inserted")
    decks.insert()
    print("decks inserted")
    matches.insert()
    print("matches inserted")
    images.insert()
    print("images inserted")
    return {"message": "neo4j seeded"}
