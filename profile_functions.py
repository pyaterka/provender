import sqlite3

def build_user_profile():
    conn = sqlite3.connect('test_recipes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    profile = {}

    cursor.execute("SELECT ingredient_name FROM pantry ORDER BY ingredient_name")
    profile['staples'] = [row["ingredient_name"] for row in cursor.fetchall()]

    cursor.execute('''
        SELECT r.name, f.rating, f.reason
        FROM feedback f
        JOIN recipes r ON r.id = f.recipe_id
        WHERE f.rating >= 4
        ORDER BY f.rating DESC
    ''')
    profile["loved"] = [dict(r) for r in cursor.fetchall()]

    cursor.execute('''
        SELECT r.name, f.rating, f.reason
        FROM feedback f
        JOIN recipes r ON r.id = f.recipe_id
        WHERE f.RATING <= 2
        ORDER BY f.rating ASC
    ''')
    profile["disliked"] = [dict(r) for r in cursor.fetchall()]

    cursor.execute('''
        SELECT r.name FROM feedback f
        JOIN recipes r ON r.id = f.recipe_id
        WHERE f.cooked = 1
    ''')
    profile["already_cooked"] = [r["name"] for r in cursor.fetchall()]

    cursor.execute("SELECT AVG(rating) as avg FROM feedback WHERE rating IS NOT NULL")
    row = cursor.fetchone()
    profile["avg_rating"] = round(row["avg"], 1) if row["avg"] else None

    conn.close()
    return profile

def format_profile_for_prompt(profile):
    lines = []

    if profile["staples"]:
        lines.append(f"Staples ({len(profile['staples'])} items): {', '.join(profile['staples'])}")

    if profile["loved"]:
        lines.append("Loved recipes: ")
        for r in profile["loved"]:
            reason = f" - {r['reason']}" if r['reason'] else ""
            lines.append(f" - {r['name']} ({r['rating']}/5){reason}")

    if profile['disliked']:
        lines.append("Disliked recipes: ")
        for r in profile["disliked"]:
            reason = f" - {r['reason']}" if r['reason'] else ""
            lines.append(f" - {r['name']} ({r['rating']}/5){reason}")

    if profile["already_cooked"]:
        lines.append(f"Already cooked: {', '.join(profile['already_cooked'])}")

    if profile["avg_rating"]:
        lines.append(f"Average rating: {profile['avg_rating']}/5")

    return "\n".join(lines) if lines else "(No profile data yet)"



        
