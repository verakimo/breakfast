PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO classification_groups (name)
VALUES ('Breakfast feature');

INSERT OR IGNORE INTO classification_groups (name)
VALUES ('Breakfast type');

INSERT OR IGNORE INTO classification_groups (name)
VALUES ('Diet');


INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'High-protein'
FROM classification_groups
WHERE name = 'Breakfast feature';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'High-carbohydrate'
FROM classification_groups
WHERE name = 'Breakfast feature';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Low-fat'
FROM classification_groups
WHERE name = 'Breakfast feature';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Festive breakfast'
FROM classification_groups
WHERE name = 'Breakfast feature';


INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Porridge'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Muesli or yogurt'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Egg dish'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Sandwich'
FROM classification_groups
WHERE name = 'Breakfast type';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Other'
FROM classification_groups
WHERE name = 'Breakfast type';


INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Lactose-free'
FROM classification_groups
WHERE name = 'Diet';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Gluten-free'
FROM classification_groups
WHERE name = 'Diet';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Vegan'
FROM classification_groups
WHERE name = 'Diet';

INSERT OR IGNORE INTO classification_options (group_id, name)
SELECT id, 'Low FODMAP'
FROM classification_groups
WHERE name = 'Diet';
