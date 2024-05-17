from pymongo import MongoClient

# Połączenie z bazą danych MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mtg"]
cards = db["cards"]
decks = db["decks"]


print("Podaj nazwę talii: ")

deckName = input()


while 1:
    print("Podaj nazwę karty: ")
    duplicate = False
    cardName = input()

    foundCard = cards.find_one({ "name": cardName })

    foundDeck = decks.find_one({ "name": deckName, "userId": 1 })

    if foundCard != None:

        foundCardId = foundCard.get('_id')

        if foundDeck == None:
            decks.insert_one({"name": deckName, "cardsId": [foundCardId], "userId": 1})

        else:
            for card in foundDeck['cardsId']:
                if card == foundCardId:
                    duplicate = True
            if duplicate:
                    print("Podana karta jest już w talii")
            else:
                result = decks.update_one({'name': deckName, "userId": 1}, {'$push': { 'cardsId': {'$each': [foundCardId]}}})
                print("Dodano kartę do talii")
                print("Obecna ilość kart w talii wynosi:", len(foundDeck['cardsId']) + 1)
    else:
        print("Podana nazwa karty jest nieprawidłowa")
        continue
