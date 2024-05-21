from fastapi import APIRouter

from app.routes import auth, cards, matches, decks, cards_collection

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(decks.router, prefix="/decks", tags=["decks"])
api_router.include_router(cards_collection.router, prefix="/cards_collection", tags=["cards_collection"])
