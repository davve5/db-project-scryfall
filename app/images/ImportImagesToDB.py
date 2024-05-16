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

# Funkcja do zapisywania danych binarnych obrazu do bazy MongoDB
def save_image_to_mongodb(image_id, base64_image):
    # Połączenie z bazą danych MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mtg"]
    collection = db["cards"]
    image_binary = base64.b64decode(base64_image)

    # Sprawdzenie, czy dokument o podanym identyfikatorze istnieje już w kolekcji
    existing_document = collection.find_one({"id": image_id})

    # Jeśli dokument istnieje, zaktualizuj dane binarne obrazu
    if existing_document:
        collection.update_one({"id": image_id}, {"$set": {"binaryImage": image_binary}})
        print('Dodano zdjecie.')
    else:
        print('Dokument o podanym ID nie istnieje.')

# Ścieżka do pliku JPG
jpg_path = "Images"

images = os.listdir(jpg_path)


for image in images:
    # Konwertowanie zdjęcia JPG na dane binarne
    base64_image = jpg_to_binary(jpg_path + "\\" + image)
    # Zapisanie danych binarnych obrazu do bazy MongoDB
    save_image_to_mongodb(image[:-4], base64_image)
    
 
#"binaryImage":""
