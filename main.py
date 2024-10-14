GET_EDGES = True
GET_ENTITIES = True

from openai import OpenAI
import os
import sqlite3
from pydantic import BaseModel
from utils import extract_edges, extract_entities

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Entity(BaseModel):
    name: str
    short_discription: str

class NamedEntities(BaseModel):
    entities: list[Entity]

class Edge(BaseModel):
    source: str
    target: str
    short_discription: str
    relation: str

class NamedEdges(BaseModel):
    edges: list[Edge]

# Database wrapper class
class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, query):
        self.cursor.execute(query)

    def insert_into_table(self, query, values):
        self.cursor.execute(query, values)

    def select_from_table(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def commit_changes(self):
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def setup_entity_table(self):
        entity_table_query = '''
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            short_discription TEXT NOT NULL
        )
        '''
        self.create_table(entity_table_query)

    def insert_entities(self, entities):
        entity_insert_query = 'INSERT INTO entities (name, short_discription) VALUES (?, ?)'
        for entity in entities:
            self.insert_into_table(entity_insert_query, (entity.name, entity.short_discription))
        self.commit_changes()

    def get_entities(self):
        entity_select_query = "SELECT name, short_discription FROM entities"
        return self.select_from_table(entity_select_query)

    def setup_edge_table(self):
        edge_table_query = '''
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            short_discription TEXT NOT NULL,
            relation TEXT NOT NULL
        )
        '''
        self.create_table(edge_table_query)

    def insert_edges(self, edges):
        edge_insert_query = 'INSERT INTO edges (source, target, short_discription, relation) VALUES (?, ?, ?, ?)'
        for edge in edges:
            try:
                if self.entity_exists(edge.source) and self.entity_exists(edge.target):
                    self.insert_into_table(edge_insert_query, (edge.source, edge.target, edge.short_discription, edge.relation))
                else:
                    print(f"Invalid edge: {edge.source} or {edge.target} does not exist in entities.")
            except Exception as e:
                print(f"Failed to insert edge: source={edge.source}, target={edge.target}, short_description={edge.short_discription}, relation={edge.relation}")
                print(f"Error: {str(e)}")
        self.commit_changes()

    def entity_exists(self, name):
        query = "SELECT id FROM entities WHERE name = ?"
        self.cursor.execute(query, (name,))
        return self.cursor.fetchone() is not None

    def get_edges(self):
        edge_select_query = "SELECT source, target, short_discription, relation FROM edges"
        return self.select_from_table(edge_select_query)

    def get_entities_and_edges(self):
        entities = self.get_entities()
        edges = self.get_edges()
        return {
            "entities": [{"name": e[0], "short_discription": e[1]} for e in entities],
            "edges": [{"source": e[0], "target": e[1], "short_discription": e[2], "relation": e[3]} for e in edges]
        }

def main():
    # Create a Database instance
    db = Database('entities.db')

    if GET_ENTITIES:
        # Read input text from transcript.txt
        with open("/home/garlan/git/agents/make_graph/transcript.txt", 'r') as file:
            text = file.read()

        # Extract entities
        result = extract_entities(text, client, NamedEntities)

        # Setup and insert entities into the database
        db.setup_entity_table()
        db.insert_entities(result.entities)

    # Retrieve and print extracted entities from the database
    entities = db.get_entities()

    for entity in entities:
        print(f"Entity: {entity[0]}, Description: {entity[1]}")

    if GET_EDGES:
        # Read input text from transcript.txt
        with open("/home/garlan/git/agents/make_graph/transcript.txt", 'r') as file:
            text = file.read()

        # Extract edges
        result = extract_edges(text, entities, client, NamedEdges)

        # Setup and insert edges into the database
        db.setup_edge_table()
        db.insert_edges(result.edges)

        print(result)

    # Close the database connection
    db.close_connection()

if __name__ == "__main__":
    main()
