from fastapi import FastAPI

from app.routes.main import api_router
from seeders import cards, users, decks, cards_collection, matches
from db.indexes import create_indexes



app = FastAPI()
create_indexes()

app.include_router(api_router)


@app.get("/seed")
async def root():
    users.insert()
    print("users inseted")
    cards.insert()
    print("cards inseted")
    cards_collection.insert()
    print("cards_collection inseted")
    decks.insert()
    print("decks inseted")
    matches.insert()
    print("matches inseted")
    return {"message": "neo4j seeded"}
