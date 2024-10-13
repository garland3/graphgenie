from openai import OpenAI
import os
import sqlite3
from pydantic import BaseModel
from typing import List

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Entity(BaseModel):
    name: str
    category: str

class NamedEntities(BaseModel):
    entities: List[Entity]

def extract_entities(text):
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",  # Use the latest available model
        messages=[
            {"role": "system", "content": "You are an expert in named entity recognition. Extract entities from the given text and categorize them."},
            {"role": "user", "content": f"Extract entities from the following text: {text}"}
        ],
        response_format={"type": "json_object"},
        schema=NamedEntities.model_json_schema()
    )

    return NamedEntities.model_validate_json(response.choices[0].message.content)

# Read input text from transcript.txt
with open('transcript.txt', 'r') as file:
    text = file.read()

# Extract entities
result = extract_entities(text)

# Connect to SQLite database (or create it)
conn = sqlite3.connect('entities.db')
cursor = conn.cursor()

# Create a table for entities
cursor.execute('''
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL
)
''')

# Insert entities into the database
for entity in result.entities:
    cursor.execute('INSERT INTO entities (name, category) VALUES (?, ?)', (entity.name, entity.category))

# Commit changes and close the connection
conn.commit()
conn.close()

# Print extracted entities
for entity in result.entities:
    print(f"Entity: {entity.name}, Category: {entity.category}")
