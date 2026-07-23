"""Database functions for breakfast recipes."""

import db


def add_recipe(title, ingredients, instructions, preparation_time, user_id):
    """Add a new recipe to the database and return its id."""
    sql = """
        INSERT INTO recipes (
            title,
            ingredients,
            instructions,
            preparation_time,
            user_id
        )
        VALUES (?, ?, ?, ?, ?)
    """
    db.execute(
        sql,
        [title, ingredients, instructions, preparation_time, user_id],
    )
    return db.last_insert_id()


def get_recipe(recipe_id):
    """Return one recipe with its author's username."""
    sql = """
        SELECT
            r.id,
            r.title,
            r.ingredients,
            r.instructions,
            r.preparation_time,
            r.created_at,
            r.user_id,
            u.username
        FROM recipes r
        JOIN users u ON u.id = r.user_id
        WHERE r.id = ?
    """
    rows = db.query(sql, [recipe_id])

    if not rows:
        return None

    return rows[0]