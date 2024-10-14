import sqlite3


def extract_entities(text, client, class_format):
    prompt = f" Given the text:\n\n{text}\n\nExctract entities and give a short discription. Respond in json"
    system_prompt = "You are an expert in named entity recognition. Extract entities from the given text and categorize them."
    
    return openai_structured_call(client, class_format, prompt, system_prompt)

def extract_edges(text, existing_entities, client, class_format):
    exsiting_entities_as_str = ""
    for entity in existing_entities:
        exsiting_entities_as_str += f"name='{entity[0]}' short_discription='({entity[1]})', \n"
        
    prompt = f" Given the text:\n\n{text}\n\nExtract relationships between the existing entities:\n\n {exsiting_entities_as_str}.\n\n Respond in json. The names of the entities are in the form of name='entity_name' short_discription='entity_short_discription'. For each relationship, provide a one-word description of the relation. You must use valid names for existing entities."
    system_prompt = "You are an expert in relationship extraction. Extract relationships between the existing entities, categorize them, and provide a one-word description of each relationship."
    return openai_structured_call(client, class_format, prompt, system_prompt)


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



