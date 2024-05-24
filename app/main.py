from fastapi import FastAPI

from app.routes.main import api_router
from seeders import cards, users, decks, cards_collection, matches, images

app = FastAPI()

app.include_router(api_router)


@app.get("/seed")
async def root():
    users.insert()
    print("users inserted")
    cards.insert()
    print("cards inserted")
    images.insert()
    print("images inserted")
    cards_collection.insert()
    print("cards_collection inserted")
    decks.insert()
    print("decks inserted")
    matches.insert()
    print("matches inserted")
    return {"message": "neo4j seeded"}
