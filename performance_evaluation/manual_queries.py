############ 5 ⚡ AGGREGATION ############

# 2 TABLES
def get_manual_test_agg_6(limit):
    return f"""
SELECT cat_name, count, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
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
                    FROM p_plays p
                    JOIN p_witnessed w ON w.cat_name = p.cat_name
                    LIMIT {limit}
                ) AS first
                GROUP BY cat_name
            ) AS second
        ) AS third
    ) AS forth
    GROUP BY cat_name, count
) AS fifth
JOIN _dict d ON d.name = 'performance'
ORDER BY cat_name;
"""

############ 6 ⚡ COUNT(*) ############

# 1 TABLE
def get_manual_test_agg_all_3(limit):
    return f"""
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
                        FROM p_witnessed
                        GROUP BY cat_name
                        LIMIT {limit}
                    ) AS first
                    GROUP BY TRUE
                ) AS second
            ) AS third
        ) AS forth
        GROUP BY count_rows
    ) AS fifth
    JOIN _dict d ON d.name = 'performance'
) AS sixth;
"""

############ 7 ⚡ FILTERS ############

# 3 TABLES
def get_manual_test_where_having_1(limit):
    return f"""
SELECT cat_name, witness, companion, caretaker, COUNT, probability, _sentence
FROM (
    SELECT cat_name, witness, companion, caretaker, COUNT, round(prob(d.dict, _sentence)::numeric, 4) AS probability, _sentence
    FROM (
        SELECT cat_name, witness, companion, caretaker, COUNT, agg_or(_sentence) AS _sentence
        FROM (
            SELECT cat_name, witness, companion, caretaker, prob_Bdd_count(arr,mask) AS COUNT, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
            FROM (
                SELECT cat_name, witness, companion, caretaker, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64) AS mask
                FROM (
                    SELECT cat_name, witness, companion, caretaker, array_agg(color) arr, array_agg(_sentence) arr_sentence
                    FROM (
                        SELECT w.cat_name, w.witness, p.companion, c.caretaker, w.color, w._sentence & p._sentence & c._sentence AS _sentence
                        FROM p_witnessed w
                        JOIN p_plays p ON w.cat_name = p.cat_name
                        JOIN p_cares c ON w.cat_name = c.cat_name
                        LIMIT {limit}
                    ) AS first
                    GROUP BY cat_name, witness, companion, caretaker
                ) AS second
            ) AS third
        ) AS forth
        GROUP BY cat_name, witness, companion, caretaker, COUNT
    ) AS fifth
    JOIN _dict d ON d.name = 'performance'
) AS sixth
ORDER BY probability ASC;
"""

############ 8 ⚡ LARGE ############

# 4 TABLES
def get_manual_test_large_query_3(limit):
    return f"""
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
                        FROM p_witnessed w
                        JOIN p_plays p ON w.cat_name = p.cat_name
                        JOIN p_cares c ON w.cat_name = c.cat_name
                        JOIN p_owns o ON w.cat_name = o.cat_name
                        LIMIT {limit}
                    ) AS first
                    GROUP BY witness, companion, caretaker, owner, cat_name
                    LIMIT {limit}
                ) AS second
            ) AS third
        ) AS forth
        GROUP BY witness, companion, caretaker, owner, cat_name, color_count
    ) AS fifth
    JOIN _dict d ON d.name = 'performance'
) AS sixth
ORDER BY witness DESC, probability ASC;
"""


def get_manual_tests(limit):
    manual_test_agg_6 = get_manual_test_agg_6(limit)
    manual_test_agg_all_3 = get_manual_test_agg_all_3(limit)
    manual_test_where_having_1 = get_manual_test_where_having_1(limit)
    manual_test_large_query_3 = get_manual_test_large_query_3(limit)

    # NOTE: We switch auto_test_agg_6 and auto_test_agg_all_3 because the former has more tables than the latter.
    return [manual_test_agg_all_3, manual_test_agg_6, manual_test_where_having_1, manual_test_large_query_3]

manual_test_names = [
    "manual_test_agg_all_3",
    "manual_test_agg_6",
    "manual_test_where_having_1",
    "manual_test_large_query_3"
]
