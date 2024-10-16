
# %%
# pip install ollama-instructor
from ollama_instructor.ollama_instructor_client import OllamaInstructorClient
from pydantic import BaseModel
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
    
my_text = "Bob is the boss of 5 people. He works at a company called Acme Corp."

prompt = my_text + "\n\n Extract the Named Entities and Edges from the text."

client = OllamaInstructorClient(host='http://localhost:11434')
response = client.chat_completion(
    model='llama3.2',
    pydantic_model=NamedEntities,
    messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ]
)

print(response['message']['content'])
# %%
