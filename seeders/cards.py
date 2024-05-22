import json
from db.mongo import MongoManager


def import_cards_to_mongo():
    mongo = MongoManager.get_instance()
    mongo['cards'].create_indexes({
        name: 1,
        color_identity: 1,
        rarity: 1,
        type_line: 1,
        legalities: 1,
        set_type: 1,
        power: 1,
        toughness: 1,
        mana_cost: 1,
    })
    # with open("/Users/dawid/__DEV__/cards.json", 'r') as file:
    # 	# Load JSON data
    # 	data = json.load(file)
    # 	res = mongo['cards'].insert_many(data)
    # 	print(res)

    # res = mongo['cards'].insert_many(file_data)
    # print(res)
# def import_cards():
# 	for document in mongo_collection.find():
# 		name = document.get('name')
# 		released_at = document.get('released_at')
# 		type_line = document.get('type_line')
# 		rarity = document.get('rarity')
# 		colors = document.get('colors', [])
# 		#prices = document.get('prices', [])

# 		# query = "CREATE (n:Card {name: $name, released_at: $released_at, type_line: $type_line, rarity: $rarity, colors: $colors})"
# 		# neo4j_session.run(query, {"name": name, "released_at": released_at, "type_line": type_line, "colors":colors, "rarity":rarity})

# import_cards()
