"""Database functions for recipe comments and ratings."""

import db


def add_comment(recipe_id, user_id, comment_text, rating):
    """Add a comment and rating to a recipe."""
    sql = """
        INSERT INTO comments (
            recipe_id,
            user_id,
            comment_text,
            rating
        )
        VALUES (?, ?, ?, ?)
    """
    db.execute(
        sql,
        [recipe_id, user_id, comment_text, rating],
    )


def get_comments(recipe_id):
    """Return a recipe's comments, newest first."""
    sql = """
        SELECT
            c.id,
            c.comment_text,
            c.rating,
            c.created_at,
            c.user_id,
            u.username
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.recipe_id = ?
        ORDER BY c.created_at DESC, c.id DESC
    """
    return db.query(sql, [recipe_id])


def get_review_summary(recipe_id):
    """Return the average rating and number of reviews."""
    sql = """
        SELECT
            COUNT(*) AS comment_count,
            COUNT(rating) AS rating_count,
            ROUND(AVG(rating), 1) AS average_rating
        FROM comments
        WHERE recipe_id = ?
    """
    rows = db.query(sql, [recipe_id])
    return rows[0]