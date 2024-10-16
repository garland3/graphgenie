import json
import sqlite3


def extract_entities(text, client, class_format, use_ollama):
    prompt = f" Given the text:\n\n{text}\n\nExtract entities and give a short description. Respond in json"
    system_prompt = "You are an expert in named entity recognition. Extract entities from the given text and categorize them."
    
    if use_ollama:
        v =  ollama_structured_call(client, class_format, prompt)
        
        # print("Type of v: ", type(v))
        
        # print(f"Ollama returned: {v}")
        v2 = class_format(**v)
        # print(f"Type of v2: {type(v2)}")
        return v2
    else:
        return openai_structured_call(client, class_format, prompt, system_prompt)

def extract_edges(text, existing_entities, client, class_format, use_ollama):
    existing_entities_as_str = ""
    for entity in existing_entities:
        existing_entities_as_str += f"name='{entity[0]}' short_description='({entity[1]})', \n"
        
    prompt = f" Given the text:\n\n{text}\n\nExtract relationships between the existing entities:\n\n {existing_entities_as_str}.\n\n Respond in json. The names of the entities are in the form of name='entity_name' short_description='entity_short_description'. For each relationship, provide a one-word description of the relation. You must use valid names for existing entities."
    system_prompt = "You are an expert in relationship extraction. Extract relationships between the existing entities, categorize them, and provide a one-word description of each relationship."
    
    if use_ollama:
        v =  ollama_structured_call(client, class_format, prompt)
        # print(f"Ollama returned: {v}")
        v2 = class_format(**v)
        # print(f"Type of v2: {type(v2)}")
        return v2
    else:
        return openai_structured_call(client, class_format, prompt, system_prompt)

def ollama_structured_call(client, class_format, prompt):
    response = client.chat_completion(
        model='llama3.2',
        pydantic_model=class_format,
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )
    return response['message']['content']

def openai_structured_call( client, class_format, prompt, system_prompt):
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",  # Use the latest available model
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        # response_format={"type": "json_object"}
        response_format=class_format,
    )
    m = response.choices[0].message
    if m.parsed:
        print(m.parsed)
        return m.parsed
    else:
        print(m.refusal)
        print("Nothing returned")
        return None



