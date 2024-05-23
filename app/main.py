from fastapi import FastAPI

from app.routes.main import api_router
from seeders import cards, users, decks, cards_collection

app = FastAPI()

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
    return {"message": "neo4j seeded"}
