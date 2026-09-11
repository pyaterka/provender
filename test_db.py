import sqlite3

def reset_database():

    # Step 1: Connect to database
    conn = sqlite3.connect('test_recipes.db')  # What filename?
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("DROP TABLE IF EXISTS steps")
    cursor.execute("DROP TABLE IF EXISTS ingredients")
    cursor.execute("DROP TABLE IF EXISTS recipes")


def reset_database():
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    
    # Enable foreign keys!
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Drop tables in REVERSE dependency order
    # (children first, then parents)
    cursor.execute("DROP TABLE IF EXISTS steps")
    cursor.execute("DROP TABLE IF EXISTS ingredients")
    cursor.execute("DROP TABLE IF EXISTS recipes")
    
    # Create recipes table (parent)
    cursor.execute('''
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            prep_time INTEGER,
            cook_time INTEGER,
            difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
            category TEXT CHECK(category IN ('breakfast', 'lunch', 'dinner'))
        )
    ''')
    
    # Create ingredients table (child)
    cursor.execute('''
        CREATE TABLE ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            amount TEXT,
            unit TEXT,
            position INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    ''')
    
    # Create steps table (child)
    cursor.execute('''
        CREATE TABLE steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            instruction TEXT NOT NULL,
            duration INTEGER,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database reset with 3 tables")

def insert_test_recipe():
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Step 1: Insert recipe
    cursor.execute('''
        INSERT INTO recipes (name, prep_time, cook_time, difficulty, category)
        VALUES (?, ?, ?, ?, ?)
    ''', ("Scrambled Eggs", 2, 5, "easy", "breakfast"))
    
    # Step 2: Get the recipe's ID
    recipe_id = cursor.lastrowid  # ← IMPORTANT! SQLite gives you the last inserted ID
    print(f"New recipe ID: {recipe_id}")
    
    # Step 3: Insert ingredients (referencing recipe_id)
    ingredients = [
        ("eggs", "3", "whole", 1),
        ("butter", "1", "tbsp", 2),
        ("salt", "1", "pinch", 3),
        ("pepper", "1", "pinch", 4),
    ]
    
    for name, amount, unit, position in ingredients:
        cursor.execute('''
            INSERT INTO ingredients (recipe_id, name, amount, unit, position)
            VALUES (?, ?, ?, ?, ?)
        ''', (recipe_id, name, amount, unit, position))
    
    # Step 4: Insert steps
    steps = [
        (1, "Crack eggs into a bowl and whisk", None),
        (2, "Melt butter in a pan over medium heat", 1),
        (3, "Pour eggs into pan, stir gently", 3),
        (4, "Season with salt and pepper, serve", None),
    ]
    
    for step_num, instruction, duration in steps:
        cursor.execute('''
            INSERT INTO steps (recipe_id, step_number, instruction, duration)
            VALUES (?, ?, ?, ?)
        ''', (recipe_id, step_num, instruction, duration))
    
    conn.commit()
    conn.close()
    print("✅ Recipe with ingredients and steps inserted")

def show_recipe_with_details():

    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute('''
        SELECT r.name, i.name, i.amount, i.unit
        FROM recipes r
        JOIN ingredients i ON i.recipe_id = r.id
        WHERE r.id = ?
    ''', (1,))

    print("=" * 70)
    recipe = cursor.fetchall()

    print("\n📖 Recipe:")
    
    print(recipe)

    conn.close()


def update_recipe():

    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE recipes
        SET difficulty = ?, last_modified = CURRENT_TIMESTAMP
        WHERE name = ?
    ''', ("medium", "Pancakes"))

    print(f"✅ Rows updated: {cursor.rowcount}")

    conn.commit()
    conn.close()

def delete_recipe():
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM recipes
        WHERE name = ?
    ''', ("Omlette",))

    print(f"✅ Rows deleted: {cursor.rowcount}")

    conn.commit()
    conn.close()



def show_recipes():

    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("=" * 70)
    print("Tables:", cursor.fetchall())
    print("=" * 70)

    cursor.execute("SELECT * FROM recipes")
    recipes = cursor.fetchall()

    print("\n📖 Recipes in database:")
    for recipe in recipes:
        print(recipe)

    print("=" * 70)
    cursor.execute("PRAGMA table_info(recipes)")
    for col in cursor.fetchall():
        print(col)

    # Step 5: Close
    conn.close()

def query_recipes():

    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("🔍 QUERY 1: All easy recipes")
    print("="*70)
    cursor.execute("SELECT id, name, difficulty, category FROM recipes WHERE difficulty = ?",
                    ("easy",))
    for row in cursor.fetchall():
        print(row)

    print("\n" + "="*70)
    print("🔍 QUERY 2: Recipes with 'cake' in name")
    print("="*70)

    cursor.execute("SELECT id, name FROM recipes WHERE name LIKE ?",
                   ("%cake%",))
    for row in cursor.fetchall():
        print(row)

    print("\n" + "="*70)
    print("🔍 QUERY 3: Recipes with cook_time under 10 min")
    print("="*70)
    cursor.execute("SELECT id, name, cook_time FROM recipes WHERE cook_time < ?", (10,))
    for row in cursor.fetchall():
        print(row)

    print("\n" + "="*70)
    print("🔍 QUERY 4: Breakfast or lunch recipes")
    print("="*70)
    cursor.execute("SELECT id, name, category FROM recipes WHERE category IN (?, ?)", ("breakfast", "lunch"))
    for row in cursor.fetchall():
        print(row)

    print("\n" + "="*70)
    print("🔍 QUERY 5: Easy recipes that cook in 15 minutes or less")
    print("="*70)
    cursor.execute('''
        SELECT id, name, difficulty, cook_time 
        FROM recipes 
        WHERE difficulty = ? AND cook_time <= ?
    ''', ("easy", 15))
    for row in cursor.fetchall():
        print(row)
    
    conn.close()
    
if __name__ == "__main__":
    reset_database()
    insert_test_recipe()
    show_recipe_with_details()