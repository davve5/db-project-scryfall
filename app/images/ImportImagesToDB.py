from PIL import Image
import io
from pymongo import MongoClient
from bson import Binary
import os
import base64

def jpg_to_binary(image_path):
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode()
    return base64_image

def save_image_to_mongodb(image_id, base64_image):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mtg"]
    collection = db["cards"]
    image_binary = base64.b64decode(base64_image)

    existing_document = collection.find_one({"id": image_id})

    if existing_document:
        collection.update_one({"id": image_id}, {"$set": {"binary_image": image_binary}})
        print('Dodano zdjecie.')
    else:
        print('Dokument o podanym ID nie istnieje.')

jpg_path = "Images"

images = os.listdir(jpg_path)


for image in images:
    base64_image = jpg_to_binary(jpg_path + "\\" + image)
    save_image_to_mongodb(image[:-4], base64_image)
    
 
