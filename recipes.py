"""Database functions for breakfast recipes."""

import db


def add_recipe(
    title,
    ingredients,
    instructions,
    preparation_time,
    user_id,
    option_ids,
):
    """Add a new recipe and its classifications."""
    connection = db.get_connection()

    try:
        recipe_sql = """
            INSERT INTO recipes (
                title,
                ingredients,
                instructions,
                preparation_time,
                user_id
            )
            VALUES (?, ?, ?, ?, ?)
        """

        result = connection.execute(
            recipe_sql,
            [
                title,
                ingredients,
                instructions,
                preparation_time,
                user_id,
            ],
        )

        recipe_id = result.lastrowid

        classification_sql = """
            INSERT INTO recipe_classifications (
                recipe_id,
                option_id
            )
            VALUES (?, ?)
        """

        connection.executemany(
            classification_sql,
            [
                (recipe_id, option_id)
                for option_id in option_ids
            ],
        )

        connection.commit()
        return recipe_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_recipes():
    """Return all recipes with diet labels, newest first."""
    sql = """
        SELECT
            r.id,
            r.title,
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
        GROUP BY r.id, r.title
        ORDER BY r.id DESC
    """
    return db.query(sql)


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


def update_recipe(
    recipe_id,
    title,
    ingredients,
    instructions,
    preparation_time,
    option_ids,
):
    """Update a recipe and its classifications."""
    connection = db.get_connection()

    try:
        recipe_sql = """
            UPDATE recipes
            SET title = ?,
                ingredients = ?,
                instructions = ?,
                preparation_time = ?
            WHERE id = ?
        """

        connection.execute(
            recipe_sql,
            [
                title,
                ingredients,
                instructions,
                preparation_time,
                recipe_id,
            ],
        )

        delete_sql = """
            DELETE FROM recipe_classifications
            WHERE recipe_id = ?
        """

        connection.execute(delete_sql, [recipe_id])

        classification_sql = """
            INSERT INTO recipe_classifications (
                recipe_id,
                option_id
            )
            VALUES (?, ?)
        """

        if option_ids:
            connection.executemany(
                classification_sql,
                [
                    (recipe_id, option_id)
                    for option_id in option_ids
                ],
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_recipe(recipe_id):
    """Delete a recipe from the database."""
    sql = """
        DELETE FROM recipes
        WHERE id = ?
    """
    db.execute(sql, [recipe_id])


def find_recipes(query, breakfast_type_id):
    """Return recipes matching the search filters."""
    sql = """
        SELECT
            r.id,
            r.title,
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
        WHERE (
            ? = ''
            OR r.title LIKE ?
            OR r.ingredients LIKE ?
            OR r.instructions LIKE ?
        )
        AND (
            ? IS NULL
            OR EXISTS (
                SELECT 1
                FROM recipe_classifications search_rc
                WHERE search_rc.recipe_id = r.id
                  AND search_rc.option_id = ?
            )
        )
        GROUP BY r.id, r.title
        ORDER BY r.id DESC
    """

    like = "%" + query + "%"

    return db.query(
        sql,
        [
            query,
            like,
            like,
            like,
            breakfast_type_id,
            breakfast_type_id,
        ],
    )


def get_classification_groups():
    """Return classification groups and their options."""
    sql = """
        SELECT
            g.id AS group_id,
            g.name AS group_name,
            o.id AS option_id,
            o.name AS option_name
        FROM classification_groups g
        JOIN classification_options o
            ON o.group_id = g.id
        ORDER BY g.id, o.id
    """
    rows = db.query(sql)

    groups = []

    for row in rows:
        if not groups or groups[-1]["id"] != row["group_id"]:
            groups.append(
                {
                    "id": row["group_id"],
                    "name": row["group_name"],
                    "options": [],
                }
            )

        groups[-1]["options"].append(
            {
                "id": row["option_id"],
                "name": row["option_name"],
            }
        )

    return groups


def get_classifications(recipe_id):
    """Return a recipe's classifications grouped by category."""
    sql = """
        SELECT
            g.name AS group_name,
            o.name AS option_name
        FROM recipe_classifications rc
        JOIN classification_options o
            ON o.id = rc.option_id
        JOIN classification_groups g
            ON g.id = o.group_id
        WHERE rc.recipe_id = ?
        ORDER BY g.id, o.id
    """
    rows = db.query(sql, [recipe_id])

    classifications = []

    for row in rows:
        if (
            not classifications
            or classifications[-1]["name"] != row["group_name"]
        ):
            classifications.append(
                {
                    "name": row["group_name"],
                    "options": [],
                }
            )

        classifications[-1]["options"].append(
            row["option_name"]
        )

    return classifications


def get_classification_option_ids(recipe_id):
    """Return ids of the classifications selected for a recipe."""
    sql = """
        SELECT option_id
        FROM recipe_classifications
        WHERE recipe_id = ?
    """
    rows = db.query(sql, [recipe_id])

    return {
        row["option_id"]
        for row in rows
    }