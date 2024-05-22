import os
from neo4j import GraphDatabase, Session

class Neo4jManager:
   __instance: Session = None

   @staticmethod
   def get_instance() -> Session:
      if Neo4jManager.__instance == None:
            Neo4jManager()
      return Neo4jManager.__instance
   def __init__(self):
      if Neo4jManager.__instance != None:
         raise Exception("This class is a singleton!")
      else:
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jgraph"))
        Neo4jManager.__instance = driver.session()