from pymongo import MongoClient
from PIL import Image
import io

def get_image_from_mongodb(imageName):
    # Połączenie z bazą danych MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mtg"]
    collection = db["cards"]

    document = collection.find_one({"name": imageName})
    if document and "binaryImage" in document:
        image_binary = document["binaryImage"]
        return image_binary
    else:
        return None

def show_image(image_binary):
    image = Image.open(io.BytesIO(image_binary))
    
    image.show()

imageName = "Fury Sliver"

image_binary = get_image_from_mongodb(imageName)

if image_binary:
    show_image(image_binary)
else:
    print("Nie znaleziono obrazu o podanej nazwie.")