############ 1 ⚡ SIMPLE ############
manual_test_join_1 = """
SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
FROM witnessed w
JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
"""

manual_test_join_2 = """
SELECT p.companion, w.witness, w.cat_name, w.color, w.breed, w.age
FROM witnessed w
JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color;
"""


############ 2 ⚡ JOIN + PROBABILITY ############
manual_test_join_3 = """
SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed,
       ROUND(prob(d.dict, w._sentence & p._sentence)::numeric, 4) AS probability
FROM witnessed w
RIGHT JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
JOIN _dict d ON d.name = 'cats_short';
"""

manual_test_join_8 = """
SELECT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name,
       ROUND(prob(d.dict, w._sentence & p._sentence & c._sentence & o._sentence)::numeric, 4) AS probability,
       (w._sentence & p._sentence & c._sentence & o._sentence) AS _sentence
FROM witnessed w
JOIN plays p ON w.cat_name = p.cat_name
JOIN cares c ON w.cat_name = c.cat_name
JOIN owns o ON w.cat_name = o.cat_name
JOIN _dict d ON d.name = 'cats_short';
"""


############ 5 ⚡ AGGREGATION ############
manual_test_agg_1 = """
SELECT cat_name, avg, round(prob(d.dict, v._sentence)::numeric, 4) AS probability, _sentence
FROM (
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
    GROUP BY cat_name, avg
) AS fifth
JOIN _dict d ON d.name = 'cats_short'
WHERE avg > 2
ORDER BY cat_name
LIMIT 10;
"""

manual_test_agg_6 = """
SELECT cat_name, count, round(prob(d.dict, v._sentence)::numeric, 4) AS probability, _sentence
FROM (
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
    GROUP BY cat_name, count
) AS fifth
JOIN _dict d ON d.name = 'cats_short'
ORDER BY cat_name;
"""


############ 4 ⚡ DISTINCT ############
manual_test_distinct_2 = """
SELECT color
FROM (
    SELECT color, round(prob(d.dict, _sentence)::numeric, 4) AS probability
    FROM (
        SELECT color, agg_or(plays._sentence) AS _sentence
        FROM plays
        GROUP BY color
    ) AS first
    JOIN _dict d ON d.name = 'cats_short'
) AS second
WHERE probability > 0.5
ORDER BY color;
"""

manual_test_distinct_4 = """ 
SELECT age, probability
FROM (
    SELECT age, round(prob(d.dict, _sentence)::numeric, 4) AS probability
    FROM (
        SELECT p.age, agg_or(p._sentence & w._sentence) AS _sentence
        FROM plays p
        JOIN witnessed w ON w.cat_name = p.cat_name
        GROUP BY p.age
    ) AS first
    JOIN _dict d ON d.name = 'cats_short'
) AS second
WHERE probability > 0.5
ORDER BY age;
"""


############ 7 ⚡ FILTERS ############
manual_test_where_1 = f"""
SELECT witness, person, cat_name, color, probability, _sentence
FROM (
    SELECT witness, person, cat_name, color, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
    FROM (
        SELECT w.witness, p.companion AS person, w.cat_name, w.color, p._sentence AS _sentence
        FROM witnessed w
        INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
        WHERE w.cat_name = 'max' AND w.color = 'gray'
    ) AS first
    JOIN _dict d ON d.name = 'cats_short'
) AS second
WHERE probability >= 0.25
ORDER BY witness DESC, probability ASC
LIMIT 10;
"""

manual_test_where_having_1 = """
SELECT cat_name, COUNT, probability, _sentence
FROM (
    SELECT cat_name, COUNT, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
    FROM (
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
                        WHERE w.color IN ('white', 'black')
                        GROUP BY cat_name, color
                    ) AS first
                    GROUP BY cat_name
                ) AS second
            ) AS third
        ) AS forth
        GROUP BY cat_name, COUNT
    ) AS fifth
    JOIN _dict d ON d.name = 'cats_short'
) AS sixth
WHERE COUNT > 0 AND probability > 0
ORDER BY probability ASC
LIMIT 10;
"""


############ 8 ⚡ LARGE ############
manual_test_large_query_1 = """
SELECT witness, player, caretaker, owner, cat_name, probability, _sentence
FROM (
    SELECT witness, player, caretaker, owner, cat_name, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
    FROM (
        SELECT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name, w._sentence & p._sentence & c._sentence & o._sentence AS _sentence
        FROM witnessed w
        JOIN plays p ON w.cat_name = p.cat_name
        JOIN cares c ON w.cat_name = c.cat_name
        JOIN owns o ON w.cat_name = o.cat_name
        WHERE w.cat_name = 'max' AND w.color = 'gray'
    ) AS first
    JOIN _dict d ON d.name = 'cats_short'
) AS second
ORDER BY witness DESC, probability ASC
LIMIT 10;
"""

manual_test_large_query_3 = """
SELECT witness, companion, caretaker, owner, cat_name, color_count, probability, _sentence
FROM (
    SELECT witness, companion, caretaker, owner, cat_name, color_count, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
    FROM (
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
        GROUP BY witness, companion, caretaker, owner, cat_name, color_count
    ) AS fifth
    JOIN _dict d ON d.name = 'cats_short'
) AS sixth
WHERE color_count > 0 AND probability > 0
ORDER BY witness DESC, probability ASC
LIMIT 10;
"""


############ 6 ⚡ COUNT(*) ############
manual_test_agg_all_3 = """
SELECT count_rows, probability, _sentence
FROM (
    SELECT count_rows, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
    FROM (
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
        GROUP BY count_rows
    ) AS fifth
    JOIN _dict d ON d.name = 'cats_short'
) AS sixth
WHERE probability > 0 AND count_rows > 0;
"""

manual_test_agg_all_5 = """
SELECT count_rows, probability, _sentence
FROM (
    SELECT count_rows, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
    FROM (
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
        GROUP BY count_rows
    ) AS fifth
    JOIN _dict d ON d.name = 'cats_short'
) AS sixth
WHERE count_rows > 0;
"""


############ 3 ⚡ MIXED DATA ############
manual_test_mixed_data_1 = """
SELECT witness, cat_id, cat_name, color, breed
FROM (
    SELECT witness, cat_id, cat_name, color, breed, round(prob(d.dict, _sentence)::numeric, 4) AS probability
    FROM (
        SELECT w.witness, pc.cat_id, w.cat_name, w.color, w.breed, w._sentence AS _sentence
        FROM witnessed w
        JOIN profile_certain pc ON w.cat_name = pc.cat_name
    ) AS first
    JOIN _dict d ON d.name = 'cats_short'
) AS second
WHERE probability > 0.5
ORDER BY cat_id;
"""

manual_test_mixed_data_3 = """
SELECT caretaker, cat_id, cat_name, breed, age, _sentence
FROM (
    SELECT c.caretaker, pc.cat_id, c.cat_name, c.breed, c.age, c._sentence & o._sentence AS _sentence
    FROM cares c
    JOIN profile_certain pc ON c.cat_name = pc.cat_name
    JOIN owns o ON c.cat_name = o.cat_name
) AS join_view
JOIN _dict d ON d.name = 'cats_short';
"""


##### All Manual Tests #####
manual_tests = {
    "SIMPLE": [
        manual_test_join_1,
        manual_test_join_2,
    ],
    "JOIN + PROBABILITY": [
        manual_test_join_3,
        manual_test_join_8,
    ],
    "AGGREGATION": [
        manual_test_agg_1,
        manual_test_agg_6,
    ],
    "DISTINCT": [
        manual_test_distinct_2,
        manual_test_distinct_4,
    ],
    "FILTERS": [
        manual_test_where_1,
        manual_test_where_having_1,
    ],
    "LARGE": [
        manual_test_large_query_1,
        manual_test_large_query_3,
    ],
    "COUNT(*)": [
        manual_test_agg_all_3,
        manual_test_agg_all_5,
    ],
    "MIXED DATA": [
        manual_test_mixed_data_1,
        manual_test_mixed_data_3,
    ]
}

manual_test_names = [
    "manual_test_join_1",
    "manual_test_join_2",
    "manual_test_join_3",
    "manual_test_join_8",
    "manual_test_agg_1",
    "manual_test_agg_6",
    "manual_test_distinct_2",
    "manual_test_distinct_4",
    "manual_test_where_1",
    "manual_test_where_having_1",
    "manual_test_large_query_1",
    "manual_test_large_query_3",
    "manual_test_agg_all_3",
    "manual_test_agg_all_5",
    "manual_test_mixed_data_1",
    "manual_test_mixed_data_3",
]
