import sqlite3

def list_all_recipes():
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()


    cursor.execute("SELECT id, name, difficulty, category FROM recipes ORDER BY id DESC")
    rows = cursor.fetchall()

    if not rows:
        print("📭 No saved recipes yet.")
        conn.close()
        return

    print("\n📚 Saved Recipes:")
    print("-" * 70)
    for row in rows:
        extras = []
        if row['difficulty']:
            extras.append(row['difficulty'])
        if row['category']:
            extras.append(row['category'])

        suffix = f" ({', '.join(extras)})" if extras else ""
        print(f"  [{row['id']}] {row['name']}{suffix}")

    print("-"*70)


    conn.close()