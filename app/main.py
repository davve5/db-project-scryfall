from fastapi import FastAPI

from app.routes.main import api_router
from seeders.cards import import_cards_to_neo4j

app = FastAPI()

app.include_router(api_router)


@app.get("/seed")
async def root():
    import_cards_to_neo4j()
    return {"message": "neo4j seeded"}
