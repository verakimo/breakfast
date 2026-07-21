PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    preparation_time INTEGER NOT NULL
        CHECK (preparation_time > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE classification_groups (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE classification_options (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL
        REFERENCES classification_groups(id),
    name TEXT NOT NULL,
    UNIQUE (group_id, name)
);

CREATE TABLE recipe_classifications (
    recipe_id INTEGER NOT NULL
        REFERENCES recipes(id) ON DELETE CASCADE,
    option_id INTEGER NOT NULL
        REFERENCES classification_options(id),
    PRIMARY KEY (recipe_id, option_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL
        REFERENCES recipes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL
        REFERENCES users(id),
    comment_text TEXT NOT NULL,
    rating INTEGER NOT NULL
        CHECK (rating BETWEEN 1 AND 5),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO classification_groups (name)
VALUES
    ('Breakfast feature'),
    ('Breakfast type'),
    ('Diet');

INSERT INTO classification_options (group_id, name)
SELECT id, 'High-protein'
FROM classification_groups
WHERE name = 'Breakfast feature';

INSERT INTO classification_options (group_id, name)
SELECT id, 'High-carbohydrate'
FROM classification_groups
WHERE name = 'Breakfast feature';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Festive breakfast'
FROM classification_groups
WHERE name = 'Breakfast feature';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Porridge'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Muesli or yogurt'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Egg dish'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Sandwich'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Other'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Lactose-free'
FROM classification_groups
WHERE name = 'Diet';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Gluten-free'
FROM classification_groups
WHERE name = 'Diet';

INSERT INTO classification_options (group_id, name)
SELECT id, 'Vegan'
FROM classification_groups
WHERE name = 'Diet';
