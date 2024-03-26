import openai
from openai import OpenAI

content = """
Classes: ['Product Category', 'Color', 'Price']
Text: {query}
Classify the user query text into the above 3 classes, like {'Product Category': 'Housewarming', 'Color': 'Red', 'Price': '50$'}. and return only the dictonary
"""


def get_text_clasification_details(model,query):
    
#     plan = aws_client.chat.completions.create(
#       model=model_name,
#       messages=[
#         {"role": "system", "content": content},
#         {"role": "user", "content": query},    
#       ]
#     )
    
    messages=[
            {"role": "system", "content": content},
            {"role": "user", "content": query},    
            ]
    openAI_client = OpenAI()
    response = openAI_client.chat.completions.create(model=model,
                          temperature=0.6,
                          messages=messages
                        )
    return response.choices[0].message.content
    
    
    