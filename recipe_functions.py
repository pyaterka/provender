import os
import json
import sqlite3

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

from prompts import save_prompt

def save_recipe(recipe):

    json_text = convert_recipe_to_json(recipe)
    if not json_text:
        print("❌ Failed to convert")
        return None

    try:
        recipe_data = json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"❌ AI returned invalid JSON: {e}")
        print(json_text)  # For debugging
        return None

    valid, message = validate_recipe_data(recipe_data)
    if not valid:
        print(f"❌ {message}")
        return None

    return save_recipe_to_db(recipe_data)

def validate_recipe_data(recipe_data):
    if not isinstance(recipe_data, dict):
        return False, "Recipe data is not a dict"

    if not recipe_data.get("name"):
        return False, "Recipe has no name"

    ingredients = recipe_data.get("ingredients", [])
    if not isinstance(ingredients, list):
        return False, "Ingredients is not a list"
    
    steps = recipe_data.get("steps", [])
    if not isinstance(steps, list):
        return False, "Steps is not a list"
    
    tags = recipe_data.get("tags", [])
    if not isinstance(tags, list):
        return False, "Tags is not a list"
    
    return True, "OK"
    
def convert_recipe_to_json(recipe):

    load_dotenv()
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        base_url="https://api.deepseek.com")

    model = os.environ.get('FORMAT_MODEL', 'deepseek-v4-flash')

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

    if not response.choices:
        print("❌ AI returned no response")
        return None  

    content = response.choices[0].message.content
    if not content:
        print("❌ AI returned empty content")
        return None

    return content


def save_recipe_to_db(recipe_data):
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    try:
        with conn:
            cursor.execute('''
                INSERT INTO recipes (name, prep_time, cook_time, difficulty, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                recipe_data.get("name"),
                recipe_data.get("prep_time"), 
                recipe_data.get("cook_time"), 
                recipe_data.get("difficulty"), 
                recipe_data.get("category")
            ))

            recipe_id = cursor.lastrowid

            for position, ing in enumerate(recipe_data.get("ingredients", []), 1):
                cursor.execute('''
                    INSERT INTO ingredients (recipe_id, name, amount, unit, position)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    recipe_id, 
                    ing.get("name"), 
                    ing.get("amount"), 
                    ing.get("unit"), 
                    position
                ))

            for step in recipe_data.get("steps", []):
                cursor.execute('''
                    INSERT INTO steps (recipe_id, step_number, instruction, duration)
                    VALUES (?, ?, ?, ?)
                ''', (
                    recipe_id,
                    step.get("step_number"),
                    step.get("instruction"),
                    step.get("duration")
                ))

            for tag_name in recipe_data.get("tags", []):
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                tag = cursor.fetchone()
            
                if not tag:
                    print(f"❌ Tag '{tag_name}' is not supported")
                    continue
            
                tag_id = tag['id']
            
                cursor.execute('''
                    INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id)
                    VALUES (?, ?)
                    ''', (recipe_id, tag_id))

        return recipe_id
    except Exception as e:
        print(f"❌ Error saving recipe: {e}")
        return None
    finally:
        conn.close()

def save_recipe_feedback(recipe_id, rating, would_make_again, reason, cooked):
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    would_make_again_int = 1 if would_make_again == 'y' else 0
    cooked_int = 1 if cooked == 'y' else 0
    cooked_at = datetime.now().isoformat() if cooked == 'y' else None

    try:
        with conn:
            cursor.execute('''
                INSERT INTO feedback (recipe_id, rating, would_make_again, reason, cooked, cooked_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(recipe_id) DO UPDATE SET
                    rating = excluded.rating,
                    would_make_again = excluded.would_make_again,
                    reason = excluded.reason,
                    cooked = excluded.cooked,
                    cooked_at = COALESCE(feedback.cooked_at, excluded.cooked_at),
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                recipe_id,
                rating,
                would_make_again_int,
                reason,
                cooked_int,
                cooked_at
            ))

            return recipe_id
    except Exception as e:
        print(f"❌ Error saving feedback: {e}")
        return None
    finally:
        conn.close()