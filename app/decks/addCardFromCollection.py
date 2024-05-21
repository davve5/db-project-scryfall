from pymongo import MongoClient

# Połączenie z bazą danych MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mtg"]
cards = db["cards"]
cardCollection = db["cardCollection"]




print("Podaj nazwę karty: ")
duplicate = False
cardName = input()

foundCard = cards.find_one({ "name": cardName })

foundCollection = cardCollection.find_one({ "userId": 1 })
    
if foundCard != None:

    foundCardId = foundCard.get('_id')
    
    if foundCollection == None:
        cardCollection.insert_one({ "userId": 1, 'cardsId': [foundCardId] })
        foundCollection = cardCollection.find_one({ "userId": 1 })
        print("Dodano kartę do talii")
        
    else:
   
        cardCollectionId = foundCollection.get('_id')

        for card in foundCollection['cardsId']:
            if card == foundCardId:
                duplicate = True
        if duplicate:
                print("Podana karta jest już w talii")
        else:
            result = cardCollection.update_one({"_id": cardCollectionId}, {'$push': { 'cardsId': {'$each': [foundCardId]}}})
            print("Dodano kartę do talii")
            print("Obecna ilość kart w kolekcji wynosi:", len(foundCollection['cardsId']) + 1)
else:
    print("Podana nazwa karty jest nieprawidłowa")
