import sqlite3

def create_database():

    # Step 1: Connect to database
    conn = sqlite3.connect('test_recipes.db')  # What filename?

    # Step 2: Create cursor
    cursor = conn.cursor()

    # Step 3: Execute SQL to create a table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
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

    # Insert a test recipe
    cursor.execute('''
        INSERT INTO recipes (name, prep_time, cook_time, difficulty, category)
        VALUES (?, ?, ?, ?, ?)
    ''', ("Pancakes", 10, 15, "easy", "breakfast"))

    # Step 4: Commit
    conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", cursor.fetchall())

    cursor.execute("SELECT * FROM recipes")
    recipes = cursor.fetchall()

    print("\n📖 Recipes in database:")
    for recipe in recipes:
        print(recipe)

    # Step 5: Close
    conn.close()

if __name__ == "__main__":
    create_database()