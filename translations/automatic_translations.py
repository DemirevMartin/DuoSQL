############ 1⚡ ############
auto_auto_test_simple_2 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT p.companion AS suspect, witness, w.color, w.cat_name
FROM witnessed w, plays p
WHERE w.color = p.color AND w.cat_name = p.cat_name;

SELECT suspect, witness, color, cat_name
FROM join_view;
"""

auto_test_join_1 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
FROM witnessed w
JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed;

SELECT person, witness, cat_name, color, breed
FROM join_view;
"""


############ 2⚡ ############
auto_test_join_3 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed, w._sentence & p._sentence AS _sentence
FROM witnessed w
RIGHT JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM join_view v, _dict d
WHERE d.name = 'cats_short';

SELECT person, witness, cat_name, color, breed, probability
FROM prob_view;
"""

auto_test_join_8 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name, w._sentence & p._sentence & c._sentence & o._sentence AS _sentence
FROM witnessed w
JOIN plays p ON w.cat_name = p.cat_name
JOIN cares c ON w.cat_name = c.cat_name
JOIN owns o ON w.cat_name = o.cat_name;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM join_view v, _dict d
WHERE d.name = 'cats_short';

SELECT witness, player, caretaker, owner, cat_name, probability, _sentence
FROM prob_view;
"""

############ 3⚡ ############
auto_test_agg_1 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS agg_view CASCADE;

CREATE OR REPLACE VIEW agg_view AS
SELECT cat_name, avg, agg_or(_sentence) AS _sentence
FROM (
    SELECT cat_name, prob_Bdd_avg(arr,mask) AS avg, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT cat_name, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64) AS mask
        FROM (
            SELECT cat_name, array_agg(age) arr, array_agg(_sentence) arr_sentence
            FROM (
                SELECT cat_name, age, agg_or(_sentence) AS _sentence
                FROM witnessed
                GROUP BY cat_name, age
            ) AS first
            GROUP BY cat_name
        ) AS second
    ) AS third
) AS forth
GROUP BY cat_name, avg;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM agg_view v, _dict d
WHERE d.name = 'cats_short';

SELECT cat_name, avg, probability, _sentence
FROM prob_view
WHERE avg > 2
ORDER BY cat_name
LIMIT 10;
"""

auto_test_agg_6 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS agg_view CASCADE;

CREATE OR REPLACE VIEW agg_view AS
SELECT cat_name, count, agg_or(_sentence) AS _sentence
FROM (
    SELECT cat_name, prob_Bdd_count(arr,mask) AS count, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT cat_name, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64) AS mask
        FROM (
            SELECT cat_name, array_agg(companion) arr, array_agg(_sentence) arr_sentence
            FROM (
                SELECT w.cat_name, companion, p._sentence & w._sentence AS _sentence
                FROM plays p
                JOIN witnessed w ON w.cat_name = p.cat_name
                WHERE w.color = p.color
            ) AS first
            GROUP BY cat_name
        ) AS second
    ) AS third
) AS forth
GROUP BY cat_name, count;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM agg_view v, _dict d
WHERE d.name = 'cats_short';

SELECT cat_name, count, probability, _sentence
FROM prob_view
ORDER BY cat_name;
"""

############ 4⚡ ############
auto_test_distinct_2 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT color, agg_or(plays._sentence) AS _sentence
FROM plays
GROUP BY color;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM join_view v, _dict d
WHERE d.name = 'cats_short';

SELECT color
FROM prob_view
WHERE probability > 0.5
ORDER BY color;
"""

auto_test_distinct_4 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT p.age, agg_or(p._sentence & w._sentence) AS _sentence
FROM plays p
JOIN witnessed w ON w.cat_name = p.cat_name
GROUP BY p.age;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM join_view v, _dict d
WHERE d.name = 'cats_short';

SELECT age
FROM prob_view
WHERE probability > 0.5
ORDER BY age;
"""


############ 5⚡ ############
auto_test_where_1 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT w.witness, p.companion AS person, w.cat_name, w.color, p._sentence AS _sentence
FROM witnessed w
INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
WHERE w.cat_name = 'max' AND w.color = 'gray';

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM join_view v, _dict d
WHERE d.name = 'cats_short';

SELECT witness, person, cat_name, color, probability, _sentence
FROM prob_view
WHERE probability >= 0.25
ORDER BY witness DESC, probability ASC
LIMIT 10;
"""

auto_test_where_having_1 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS agg_view CASCADE;

CREATE OR REPLACE VIEW agg_view AS
SELECT cat_name, COUNT, agg_or(_sentence) AS _sentence
FROM (
    SELECT cat_name, prob_Bdd_count(arr,mask) AS COUNT, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT cat_name, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64) AS mask
        FROM (
            SELECT cat_name, array_agg(color) arr, array_agg(_sentence) arr_sentence
            FROM (
                SELECT cat_name, color, agg_or(_sentence) AS _sentence
                FROM witnessed
                WHERE color IN ('white', 'black')
                GROUP BY cat_name, color
            ) AS first
            GROUP BY cat_name
        ) AS second
    ) AS third
) AS forth
GROUP BY cat_name, COUNT;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM agg_view v, _dict d
WHERE d.name = 'cats_short';

SELECT cat_name, COUNT, probability, _sentence
FROM prob_view
WHERE COUNT > 0 AND probability > 0
ORDER BY probability ASC
LIMIT 10;
"""


############ 6⚡ ############
auto_test_large_query_1 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name, w._sentence & p._sentence & c._sentence & o._sentence AS _sentence
FROM witnessed w
JOIN plays p ON w.cat_name = p.cat_name
JOIN cares c ON w.cat_name = c.cat_name
JOIN owns o ON w.cat_name = o.cat_name
WHERE w.cat_name = 'max' AND w.color = 'gray';

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM join_view v, _dict d
WHERE d.name = 'cats_short';

SELECT witness, player, caretaker, owner, cat_name, probability, _sentence
FROM prob_view
ORDER BY witness DESC, probability ASC
LIMIT 10;
"""

auto_test_large_query_3 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS agg_view CASCADE;

CREATE OR REPLACE VIEW agg_view AS
SELECT witness, companion, caretaker, owner, cat_name, color_count, agg_or(_sentence) AS _sentence
FROM (
    SELECT witness, companion, caretaker, owner, cat_name, prob_Bdd_count(arr,mask) AS color_count, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT witness, companion, caretaker, owner, cat_name, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64) AS mask
        FROM (
            SELECT witness, companion, caretaker, owner, cat_name, array_agg(color) arr, array_agg(_sentence) arr_sentence
            FROM (
                SELECT w.witness, p.companion, c.caretaker, o.owner, w.cat_name, w.color, w._sentence & p._sentence & c._sentence & o._sentence AS _sentence
                FROM witnessed w
                JOIN plays p ON w.cat_name = p.cat_name
                JOIN cares c ON w.cat_name = c.cat_name
                JOIN owns o ON w.cat_name = o.cat_name
                WHERE w.cat_name = 'max'
            ) AS first
            GROUP BY witness, companion, caretaker, owner, cat_name
        ) AS second
    ) AS third
) AS forth
GROUP BY witness, companion, caretaker, owner, cat_name, color_count;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM agg_view v, _dict d
WHERE d.name = 'cats_short';

SELECT witness, companion, caretaker, owner, cat_name, color_count, probability, _sentence
FROM prob_view
WHERE probability > 0 AND color_count > 0
ORDER BY witness DESC, probability ASC
LIMIT 10;
"""


############ 7⚡ ############
auto_test_one_cell_3 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS agg_all_view CASCADE;

CREATE OR REPLACE VIEW agg_all_view AS
SELECT count_rows, agg_or(_sentence) AS _sentence
FROM (
    SELECT prob_Bdd_count(arr,mask) AS count_rows, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64) AS mask
        FROM (
            SELECT array_agg(cat_name) arr, array_agg(_sentence) AS arr_sentence
            FROM (
                SELECT cat_name, agg_or(_sentence) AS _sentence
                FROM witnessed
                WHERE cat_name = 'max'
                GROUP BY cat_name
            ) AS first
            GROUP BY TRUE
        ) AS second
    ) AS third
) AS forth
GROUP BY count_rows;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM agg_all_view v, _dict d
WHERE d.name = 'cats_short';

SELECT count_rows, probability, _sentence
FROM prob_view
WHERE probability > 0 AND count_rows > 0;
"""

auto_test_one_cell_5 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS agg_all_view CASCADE;

CREATE OR REPLACE VIEW agg_all_view AS
SELECT count_rows, agg_or(_sentence) AS _sentence
FROM (
    SELECT prob_Bdd_count(arr,mask) AS count_rows, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64) AS mask
        FROM (
            SELECT array_agg(cat_name) arr, array_agg(_sentence) AS arr_sentence
            FROM (
                SELECT w.cat_name, w._sentence & p._sentence AS _sentence
                FROM witnessed w
                JOIN plays p ON w.cat_name = p.cat_name
                WHERE p.color IN ('gray', 'black')
            ) AS first
            GROUP BY TRUE
        ) AS second
    ) AS third
) AS forth
GROUP BY count_rows;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM agg_all_view v, _dict d
WHERE d.name = 'cats_short';

SELECT count_rows, probability, _sentence
FROM prob_view
WHERE count_rows > 0;
"""


############ 8⚡ ############
auto_test_mixed_data_1 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT w.witness, pc.cat_id, w.cat_name, w.color, w.breed, w._sentence AS _sentence
FROM witnessed w
JOIN profile_certain pc ON w.cat_name = pc.cat_name;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM join_view v, _dict d
WHERE d.name = 'cats_short';

SELECT witness, cat_id, cat_name, color, breed
FROM prob_view
WHERE probability > 0.5
ORDER BY cat_id;
"""

auto_test_mixed_data_3 = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;

CREATE OR REPLACE VIEW join_view AS
SELECT c.caretaker, pc.cat_id, c.cat_name, c.breed, c.age, c._sentence & o._sentence AS _sentence
FROM cares c
JOIN profile_certain pc ON c.cat_name = pc.cat_name
JOIN owns o ON c.cat_name = o.cat_name;

SELECT caretaker, cat_id, cat_name, breed, age, _sentence
FROM join_view;
"""
