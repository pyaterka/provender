import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import save_prompt

def save_recipe(recipe):

    load_dotenv()
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        base_url="https://api.deepseek.com")

    model = os.environ.get('FORMAT_MODEL')

    messages =[
        {"role": "system", "content": save_prompt},
        {"role": "user", "content": recipe}
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )
    except Exception as e:
        print(f"Error : {e}")
        return None

    return response.choices[0].message.content  