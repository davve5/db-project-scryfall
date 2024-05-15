
def import_cards():
	for document in mongo_collection.find():
		name = document.get('name')
		released_at = document.get('released_at')
		type_line = document.get('type_line')
		rarity = document.get('rarity')
		colors = document.get('colors', [])
		#prices = document.get('prices', [])

		# query = "CREATE (n:Card {name: $name, released_at: $released_at, type_line: $type_line, rarity: $rarity, colors: $colors})"
		# neo4j_session.run(query, {"name": name, "released_at": released_at, "type_line": type_line, "colors":colors, "rarity":rarity})

import_cards()
