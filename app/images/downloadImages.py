import json, requests
 
with open('default-cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)
 
for card in cards:
    if card['lang'] == 'en':
        try:
            r = requests.get(card['image_uris']['normal'])
            card_name=card["id"] + '.jpg'
            open('Images/' + card_name, 'wb').write(r.content)
        except:
            continue
        