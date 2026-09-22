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

def show_recipe(recipe_id: int):
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_key = ON")

    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    recipe = cursor.fetchone()

    if not recipe:
        print(f"❌ Recipe {recipe_id} not found.")
        conn.close()
        return

    print("\n" + "=" * 70)
    print(f"📖 {recipe['name']}")
    print("=" * 70)

    info_parts = []
    if recipe['category']:
        info_parts.append(f"Category: {recipe['category']}")
    if recipe['difficulty']:
        info_parts.append(f"Difficulty: {recipe['difficulty']}")
    if info_parts:
        print("   " + " | ".join(info_parts))

    prep = recipe['prep_time'] if recipe['prep_time'] is not None else "-"
    cook = recipe['cook_time'] if recipe['cook_time'] is not None else "-"
    print(f"   Prep: {prep} min | Cook: {cook} min")
    print(f"   Created: {recipe['created_at']}")
    print("=" * 70)

    cursor.execute ('''
        SELECT name, amount, unit, position
        FROM ingredients
        WHERE recipe_id = ?
        ORDER BY position
    ''', (recipe_id,))
    ingredients = cursor.fetchall()

    if ingredients:
        print("\n🥕 Ingredients:")
        for ing in ingredients:
            parts = [p for p in [ing['amount'], ing['unit'], ing['name']] if p]
            print(f"   {ing['position']}. {' '.join(parts)}")
    else:
        print("\n🥕 Ingredients: (none)")

    cursor.execute('''
        SELECT step_number, instruction, duration
        FROM steps
        WHERE recipe_id = ?
        ORDER BY step_number
    ''', (recipe_id,))
    steps = cursor.fetchall()

    if steps:
        print("\n📝 Steps:")
        for step in steps:
            duration = f" ({step['duration']} min)" if step['duration'] else ""
            print(f"   {step['step_number']}. {step['instruction']}{duration}")
    else:
        print("\n📝 Steps (none)")

    cursor.execute('''
        SELECT t.name
        FROM tags t
        JOIN recipe_tags rt ON rt.tag_id = t.id
        WHERE rt.recipe_id = ?
    ''', (recipe_id,))
    tags = [row['name'] for row in cursor.fetchall()]

    if tags:
        print(f"\n🏷️ Tags: {', '.join(tags)}")

    print("\n" + "=" * 70)
    conn.close()




    

