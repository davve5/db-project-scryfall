from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["mtg"]
cards = db["cards"]
decks = db["decks"]
users = db["users"]


target_color = 'G'  
deckName = "masterOfNone G2"
userName = "masterOfNone"


query = {'colors': {'$in': [target_color]}}


sample_size = 40
pipeline = [
    {'$match': query},
    {'$sample': {'size': sample_size}}
]


random_documents = list(cards.aggregate(pipeline))

foundLogin = users.find_one({ "username": userName })

foundLoginId = foundLogin.get('_id')





for doc in random_documents:
    card_id = doc.get('_id')
    foundDeck = decks.find_one({ "name": deckName, "user_id": foundLoginId })
    if foundDeck == None:
        decks.insert_one({"name": deckName, "cards_id": [card_id], "user_id": foundLoginId})
    else:
        decks.update_one({'name': deckName, "user_id": foundLoginId}, {'$push': { 'cards_id': {'$each': [card_id]}}})
