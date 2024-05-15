from neo4j import GraphDatabase

class Neo4jManager:
   __instance = None

   @staticmethod
   def get_instance():
      if Neo4jManager.__instance == None:
            Neo4jManager()
      return Neo4jManager.__instance
   def __init__(self):
      if MongoManager.__instance != None:
         raise Exception("This class is a singleton!")
      else:
        driver = GraphDatabase.driver(
					os.getenv("NEO4J_URL", "bolt://localhost:7687"),
					auth=(os.getenv("NEO4J_LOGIN", "neo4j"), os.getenv("NEO4J_PASSWORD", "neo4jgraph"))
				)
        Neo4jManager.__instance = driver.session()