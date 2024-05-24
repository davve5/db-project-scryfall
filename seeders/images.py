import json
from db.mongo import MongoManager
from db.neo4j import Neo4jManager
from pymongo import MongoClient
import requests
import os
import base64
import shutil

def jpg_to_binary(image_path):
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode()
    return base64_image

def save_image_to_mongodb(image_id, base64_image):
    mongo = MongoManager.get_instance()
    
    image_binary = base64.b64decode(base64_image)

    existing_document = mongo['cards'].find_one({"id": image_id})

    if existing_document:
        mongo['cards'].update_one({"id": image_id}, {"$set": {"binary_image": image_binary}})
        print('Dodano zdjecie.')
    else:
        print('Dokument o podanym ID nie istnieje.')





def insert():
    mongo = MongoManager.get_instance()
    jpg_path = "Images"
    try:
        os.makedirs(jpg_path)
    
        for card in mongo["cards"].find():
            if card['lang'] == 'en':
                try:
                    r = requests.get(card['image_uris']['normal'])
                    card_name=card["id"] + '.jpg'
                    open(jpg_path + '/' + card_name, 'wb').write(r.content)
                except:
                    continue
                    


        images = os.listdir(jpg_path)


        for image in images:
            base64_image = jpg_to_binary(jpg_path + "\\" + image)
            save_image_to_mongodb(image[:-4], base64_image)


        shutil.rmtree(jpg_path)
    except:
        print('Dokument o podanym ID nie istnieje.')
