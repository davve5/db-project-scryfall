from fastapi import APIRouter

from app.routes import auth, cards, matches

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
