"""Database functions for user profile pages."""

import db


def get_user(user_id):
    """Return one user and information about their profile image."""
    sql = """
        SELECT
            id,
            username,
            image IS NOT NULL AS has_image
        FROM users
        WHERE id = ?
    """
    rows = db.query(sql, [user_id])

    if not rows:
        return None

    return rows[0]


def get_recipes(user_id):
    """Return recipes added by one user with diet labels."""
    sql = """
        SELECT
            r.id,
            r.title,
            r.created_at,
            MAX(
                CASE
                    WHEN cg.name = 'Diet'
                     AND co.name = 'Lactose-free'
                    THEN 1
                    ELSE 0
                END
            ) AS lactose_free,
            MAX(
                CASE
                    WHEN cg.name = 'Diet'
                     AND co.name = 'Gluten-free'
                    THEN 1
                    ELSE 0
                END
            ) AS gluten_free,
            MAX(
                CASE
                    WHEN cg.name = 'Diet'
                     AND co.name = 'Vegan'
                    THEN 1
                    ELSE 0
                END
            ) AS vegan,
            MAX(
                CASE
                    WHEN cg.name = 'Diet'
                     AND co.name = 'Low FODMAP'
                    THEN 1
                    ELSE 0
                END
            ) AS low_fodmap
        FROM recipes r
        LEFT JOIN recipe_classifications rc
            ON rc.recipe_id = r.id
        LEFT JOIN classification_options co
            ON co.id = rc.option_id
        LEFT JOIN classification_groups cg
            ON cg.id = co.group_id
        WHERE r.user_id = ?
        GROUP BY r.id, r.title, r.created_at
        ORDER BY r.created_at DESC, r.id DESC
    """
    return db.query(sql, [user_id])


def update_image(user_id, image):
    """Save a profile image for a user."""
    sql = """
        UPDATE users
        SET image = ?
        WHERE id = ?
    """
    db.execute(sql, [image, user_id])


def get_image(user_id):
    """Return a user's profile image or None."""
    sql = """
        SELECT image
        FROM users
        WHERE id = ?
    """
    rows = db.query(sql, [user_id])

    if not rows:
        return None

    return rows[0]["image"]


def delete_image(user_id):
    """Delete a user's profile image."""
    sql = """
        UPDATE users
        SET image = NULL
        WHERE id = ?
    """
    db.execute(sql, [user_id])