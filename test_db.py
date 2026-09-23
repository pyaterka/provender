import sqlite3



def reset_database():
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    
    # Enable foreign keys!
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Drop tables in REVERSE dependency order
    # (children first, then parents)
    cursor.execute("DROP TABLE IF EXISTS recipe_tags")
    cursor.execute("DROP TABLE IF EXISTS steps")
    cursor.execute("DROP TABLE IF EXISTS ingredients")
    cursor.execute("DROP TABLE IF EXISTS tags")
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

    cursor.execute('''
        CREATE TABLE tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT
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

    cursor.execute('''
        CREATE TABLE recipe_tags (
            recipe_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (recipe_id, tag_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database reset with 3 tables")

def add_feedback_table():
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("DROP TABLE IF EXISTS feedback")

    cursor.execute('''
        CREATE TABLE feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL UNIQUE,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            would_make_again BOOLEAN,
            reason TEXT,
            cooked BOOLEAN DEFAULT 0,
            cooked_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ New table feedback added to test_db.py")

def add_pantry_table():
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute('''
        CREATE TABLE pantry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_name TEXT NOT NULL UNIQUE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            auto_added BOOLEAN DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ New table pantry added to test_db.py")

def insert_test_tags():
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    tags = [
        ("quick", "method"),
        ("healthy", "dietary"),
        ("slow-cooker", "method"),
        ("vegan", "dietary"),
        ("comfort-food", "mood"),
        ("breakfast", "meal"),
    ]

    for name, category in tags:
        cursor.execute('''
            INSERT INTO tags (name, category) VALUES (?, ?)
        ''', (name, category))

    conn.commit()
    conn.close()
    print(f"✅ {len(tags)} tags inserted")


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

def tag_recipe(recipe_id, tag_name):
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    tag = cursor.fetchone()

    if not tag:
        print(f"❌ Tag '{tag_name}' doesn't exist")
        conn.close()
        return

    tag_id = tag[0]

    cursor.execute('''
        INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id)
        VALUES (?, ?)
        ''', (recipe_id, tag_id,))

    conn.commit()
    conn.close()
    print(f"✅ Tagged recipe {recipe_id} with '{tag_name}'")

def find_recipes_by_tag(tag_name): 
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.id, r.name
        FROM recipes r
        JOIN recipe_tags rt ON rt.recipe_id = r.id
        JOIN tags t ON t.id = rt.tag_id
        WHERE t.name = ?
    ''', (tag_name,))

    print(f"\n🏷️  Recipes tagged '{tag_name}':")
    for row in cursor.fetchall():
        print(f"   [{row['id']}] {row['name']}")
    
    conn.close()

def show_recipe_tags(recipe_id): 
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT t.name
        FROM tags t
        JOIN recipe_tags rt ON rt.tag_id = t.id
        WHERE rt.recipe_id = ?
    ''', (recipe_id,))

    tags = [row['name'] for row in cursor.fetchall()]
    print(f"Recipe {recipe_id} tags: {', '.join(tags) if tags else 'none'}")
    
    conn.close()

def find_recipes_with_all_tags(*tag_names): 
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    placeholders = ','.join('?' for _ in tag_names)

    cursor.execute(f'''
        SELECT r.id, r.name
        FROM recipes r
        JOIN recipe_tags rt ON rt.recipe_id = r.id
        JOIN tags t ON t.id = rt.tag_id
        WHERE t.name IN ({placeholders})
        GROUP BY r.id
        HAVING COUNT(DISTINCT t.name) = ?
    ''', (*tag_names, len(tag_names)))

    print(f"\n🏷️  Recipes with ALL tags {tag_names}:")
    for row in cursor.fetchall():
        print(f"   [{row['id']}] {row['name']}")
    
    conn.close()



def show_recipe(recipe_id):
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    recipe = cursor.fetchone()

    if not recipe:
        print(f"❌ Recipe {recipe_id} not found")
        conn.close()
        return

    (recipe_id, name, created, modified, prep, cook, difficulty, category) = recipe

    print("\n" + "=" * 70)
    print(f"📖 Recipe: {name}")
    print("="*70)
    print(f"   Category: {category} | Difficulty: {difficulty}")
    print(f"   Prep: {prep} min | Cook: {cook} min")
    print(f"   Created: {created}")
    print("="*70)

    cursor.execute('''
        SELECT name, amount, unit, position
        FROM ingredients
        WHERE recipe_id = ?
        ORDER BY position
        ''', (recipe_id,))
    ingredients = cursor.fetchall()

    print("\n🥕 Ingredients:")
    for ing in ingredients:
        ing_name, amount, unit, position = ing
        if amount and unit:
            print(f"   {position}. {amount} {unit} {ing_name}")
        elif amount:
            print(f"   {position}. {amount} {ing_name}")
        else:
            print(f"   {position}. {ing_name}")

    cursor.execute('''
        SELECT step_number, instruction, duration 
        FROM steps 
        WHERE recipe_id = ? 
        ORDER BY step_number
    ''', (recipe_id,))
    steps = cursor.fetchall()
    
    print("\n📝 Steps:")
    for step in steps:
        step_num, instruction, duration = step
        if duration:
            print(f"   {step_num}. {instruction} ({duration} min)")
        else:
            print(f"   {step_num}. {instruction}")
    
    print("\n" + "="*70)
    conn.close()

    
def show_recipe_with_details():

    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    

    cursor.execute('''
        SELECT r.name AS recipe_name, i.name AS ingredient_name, i.amount, i.unit
        FROM recipes r
        JOIN ingredients i ON i.recipe_id = r.id
        WHERE r.id = ?
    ''', (1,))

   
    rows = cursor.fetchall()

    if not rows:
        print("❌ Recipe not found")
        conn.close()
        return

    recipe_name = rows[0]['recipe_name']
    print(f"\n📖 Recipe: {recipe_name}")
    
    for row in rows:
        print(f"  - {row['amount']} {row['unit']} {row['ingredient_name']}")

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

def recipe_stats():

    conn = sqlite3.connect("test_recipes.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            r.name,
            COUNT(DISTINCT i.id) as ingredient_count,
            COUNT(DISTINCT s.id) as step_count
        FROM recipes r
        LEFT JOIN ingredients i ON i.recipe_id = r.id
        LEFT JOIN steps s ON s.recipe_id = r.id
        GROUP BY r.id
    ''')

    print("\n📊 Recipe Statistics:")
    for row in cursor.fetchall():
        name, ing_count, step_count = row
        print(f"   {name}: {ing_count} ingredients, {step_count} steps")
    
    conn.close()

def test_cascade():
    """Test that deleting a recipe removes its ingredients/steps"""
    conn = sqlite3.connect('test_recipes.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Count before
    cursor.execute("SELECT COUNT(*) FROM ingredients WHERE recipe_id = 1")
    before = cursor.fetchone()[0]
    
    # Delete recipe
    cursor.execute("DELETE FROM recipes WHERE id = 1")
    
    # Count after
    cursor.execute("SELECT COUNT(*) FROM ingredients WHERE recipe_id = 1")
    after = cursor.fetchone()[0]
    
    print(f"Ingredients before delete: {before}")
    print(f"Ingredients after delete: {after}")  # Should be 0!
    
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    add_feedback_table()