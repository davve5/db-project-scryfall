from pymongo import MongoClient

# Połączenie z bazą danych MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mtg"]
cards = db["cards"]
decks = db["decks"]


foundCard = cards.find_one({ "name": 'Goblin Bowling Team' })

foundCardId = foundCard.get('_id')

decks.insert_one({"deckName": "Test", "cardId": foundCardId, "userId": 1})

