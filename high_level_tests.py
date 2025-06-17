from main import generate_full_translation

# NOTE NOTE DISCLAIMER: Some, mostly the general simple tests, are not included in the experiments. 
# Check the NOTE DISCLAIMER in complexity_count in experiment_runner.py for more details.

############## GENERAL SIMPLE TESTS ##############
high_level_test_simple_1 = """
    SELECT p.companion AS suspect, witness, w.color, w.cat_name
    FROM witnessed w, plays p
    WHERE w.color = p.color AND w.cat_name = p.cat_name
    HAVING probability > 0.1
    SHOW SENTENCE, PROBABILITY
"""

# Basic join with no extras
high_level_test_simple_2 = """ 
    SELECT p.companion AS suspect, witness, w.color, w.cat_name
    FROM witnessed w, plays p
    WHERE w.color = p.color AND w.cat_name = p.cat_name
"""

# Same join, showing probabilities
high_level_test_simple_3 = """
    select p.companion as suspect, witness, w.color, w.cat_name
    from witnessed w, plays p
    where w.color = p.color and w.cat_name = p.cat_name
    show probability
"""

# Same join, showing sentence
high_level_test_simple_4 = """
    SELECT p.companion AS suspect, witness, w.color, w.cat_name
    FROM witnessed w, plays p
    WHERE w.color = p.color AND w.cat_name = p.cat_name
    SHOW SENTENCE
"""

high_level_test_simple_5 = """
    SELECT *
    FROM witnessed
"""


############## JOIN ##############
# 1⚡
high_level_test_join_1 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
"""

# 1⚡
high_level_test_join_2 = """
    SELECT p.companion, w.witness, w.cat_name, w.color, w.breed, w.age
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
"""

# 2⚡
high_level_test_join_3 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    RIGHT JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
    SHOW PROBABILITY
"""

high_level_test_join_4 = """
    SELECT w.witness, p.companion AS person, w.cat_name
    FROM witnessed w 
    FULL JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    SHOW SENTENCE
"""

high_level_test_join_5 = """
    SELECT w.witness, p.companion AS person, p.cat_name
    FROM witnessed w FULL OUTER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    SHOW PROBABILITY
"""

high_level_test_join_6 = """
    SELECT w.witness, c.caretaker AS person, w.cat_name, w.color
    FROM witnessed w INNER JOIN cares c
    ON w.cat_name = c.cat_name AND w.breed = c.breed
    SHOW SENTENCE
"""

high_level_test_join_7 = """
    SELECT w.witness, p.companion AS player, c.caretaker, w.cat_name
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name
    FULL OUTER JOIN cares c ON w.cat_name = c.cat_name
    SHOW SENTENCE
"""

# 2 ⚡
high_level_test_join_8 = """
    SELECT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    JOIN cares c ON w.cat_name = c.cat_name
    JOIN owns o ON w.cat_name = o.cat_name
    SHOW SENTENCE, PROBABILITY
"""

############## ORDER BY and LIMIT ##############
high_level_test_order_limit_1 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    HAVING probability > 0.5
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE
"""

high_level_test_order_limit_2 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    LEFT OUTER JOIN plays p ON w.cat_name = p.cat_name AND w.breed = p.breed
    HAVING probability > 0.5
    ORDER BY probability DESC, w.witness ASC
    LIMIT 5
    SHOW PROBABILITY
"""

############### UN/CERTAIN Data ##############
# 8⚡
high_level_test_mixed_data_1 = """
    SELECT w.witness, pc.cat_id, w.cat_name, w.color, w.breed
    FROM witnessed w
    JOIN profile_certain pc ON w.cat_name = pc.cat_name
    HAVING probability > 0.5
    ORDER BY pc.cat_id;
"""

high_level_test_mixed_data_2 = """
    SELECT p.companion, pc.cat_id, p.cat_name, p.color
    FROM plays p
    JOIN profile_certain pc ON p.cat_name = pc.cat_name
    SHOW PROBABILITY
    LIMIT 10;
    
"""

# 8⚡
high_level_test_mixed_data_3 = """
    SELECT c.caretaker, pc.cat_id, c.cat_name, c.breed, c.age
    FROM cares c
    JOIN profile_certain pc ON c.cat_name = pc.cat_name
    JOIN owns o ON c.cat_name = o.cat_name
    SHOW SENTENCE;
"""

############## AGGREGATION ##############
# 3⚡
high_level_test_agg_1 = """
    SELECT cat_name, avg(age)
    FROM witnessed
    GROUP BY cat_name
    HAVING avg(age) > 2
    ORDER BY cat_name
    LIMIT 10
    SHOW PROBABILITY
"""

# Multiple GROUP BY
high_level_test_agg_2 = """
    SELECT cat_name, breed, avg(age)
    FROM witnessed
    GROUP BY cat_name, breed
    HAVING avg(age) > 2
    ORDER BY cat_name
    LIMIT 10
    SHOW PROBABILITY
"""

high_level_test_agg_3 = """
    SELECT w.cat_name, SUM(w.age) as total
    FROM owns o
    JOIN witnessed w ON o.cat_name = w.cat_name
    JOIN plays p ON w.cat_name = p.cat_name
    WHERE p.color IN ('gray', 'black')
    GROUP BY w.cat_name
    HAVING probability > 0
    ORDER BY probability DESC
    LIMIT 10
    SHOW PROBABILITY
"""

high_level_test_agg_4 = """
    SELECT w.cat_name, MIN(w.age) as minimum
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    WHERE p.color IN ('gray', 'black')
    GROUP BY w.cat_name
"""

high_level_test_agg_5 = """
    SELECT w.cat_name, count(companion)
    FROM plays p, witnessed w
    WHERE w.cat_name = p.cat_name
    GROUP BY w.cat_name
    ORDER BY w.cat_name
    SHOW SENTENCE, PROBABILITY
"""

# 3⚡
high_level_test_agg_6 = """
    SELECT w.cat_name, count(companion)
    FROM plays p
    JOIN witnessed w ON w.cat_name = p.cat_name
    WHERE w.color = p.color
    GROUP BY w.cat_name
    ORDER BY w.cat_name
    SHOW SENTENCE, PROBABILITY
"""


high_level_test_agg_7 = """
    SELECT w.cat_name, MAX(w.age) as minimum
    FROM owns o
    JOIN witnessed w ON o.cat_name = w.cat_name
    JOIN plays p ON w.cat_name = p.cat_name
    WHERE p.color IN ('gray', 'black')
    GROUP BY w.cat_name
    HAVING probability > 0
    SHOW PROBABILITY
"""


############## DISTINCT ##############
high_level_test_distinct_1 = """
    SELECT DISTINCT breed
    FROM witnessed;
"""

# 4⚡
high_level_test_distinct_2 = """
    SELECT DISTINCT color
    FROM plays
    HAVING probability > 0.5
    ORDER BY color;
"""

high_level_test_distinct_3 = """
    SELECT DISTINCT p.age
    FROM plays p, witnessed w
    WHERE w.cat_name = p.cat_name
    HAVING probability > 0.5
    ORDER BY p.age;
"""

# 4⚡
high_level_test_distinct_4 = """ 
    SELECT DISTINCT p.age
    FROM plays p
    JOIN witnessed w ON w.cat_name = p.cat_name
    HAVING probability > 0.5
    ORDER BY p.age;
"""

high_level_test_distinct_5 = """
    SELECT DISTINCT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    JOIN cares c ON w.cat_name = c.cat_name
    JOIN owns o ON w.cat_name = o.cat_name
    SHOW SENTENCE, PROBABILITY
"""

############### WHERE and HAVING ##############
# 5⚡
high_level_test_where_1 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    WHERE w.cat_name = 'max' AND w.color = 'gray'
    HAVING probability >= 0.25
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

high_level_test_where_2 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    LEFT OUTER JOIN plays p ON w.cat_name = p.cat_name AND w.breed = p.breed
    WHERE w.cat_name = 'max' AND (w.color = 'gray' OR w.color = 'black')
    HAVING probability > 0.3
    ORDER BY probability DESC, w.witness ASC
    LIMIT 5
    SHOW PROBABILITY
"""

# 5⚡
high_level_test_where_having_1 = """
    SELECT cat_name, COUNT(color)
    FROM witnessed
    WHERE color IN ('white', 'black')
    GROUP BY cat_name
    HAVING COUNT(color) > 0 AND probability > 0
    ORDER BY probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

high_level_test_where_having_2 = """
    SELECT cat_name, avg(age)
    FROM witnessed
    GROUP BY cat_name
    HAVING avg(age) > 2 AND probability > 0
    ORDER BY cat_name
    SHOW PROBABILITY
"""


############ CERTAIN DATA TESTS ##############
high_level_test_certain_data_1 = """
    SELECT *
    FROM profile_certain pc
"""

high_level_test_certain_data_2 = """
    SELECT pc.cat_id, pc.cat_name
    FROM profile_certain pc
    WHERE pc.cat_name = 'max'
    ORDER BY pc.cat_name
    SHOW SENTENCE, PROBABILITY
"""

# Triggers an error which is expected behavior
high_level_test_certain_data_3 = """
    SELECT pc.cat_id, pc.cat_name
    FROM profile_certain pc
    WHERE pc.cat_name = 'max'
    HAVING probability > 0.5 
    ORDER BY pc.cat_name
    SHOW SENTENCE, PROBABILITY
"""

############### LARGE QUERY TESTS ##############
# 6⚡
high_level_test_large_query_1 = """
    SELECT w.witness, plays.companion AS player, c.caretaker, o.owner, w.cat_name
    FROM witnessed w
    JOIN plays ON w.cat_name = plays.cat_name
    JOIN cares c ON w.cat_name = c.cat_name
    JOIN owns o ON w.cat_name = o.cat_name
    WHERE w.cat_name = 'max' AND w.color = 'gray'
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE,  PROBABILITY
"""

high_level_test_large_query_2 = """
    SELECT w.witness, p.companion AS player, count(w.color) AS color_count
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    WHERE w.cat_name = 'max'
    GROUP BY w.witness, p.companion, w.cat_name
    HAVING probability > 0 AND color_count > 0
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

# 6⚡
high_level_test_large_query_3 = """
    SELECT w.witness, p.companion AS player, c.caretaker, o.owner, count(w.color) AS color_count
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    JOIN cares c ON w.cat_name = c.cat_name
    JOIN owns o ON w.cat_name = o.cat_name
    WHERE w.cat_name = 'max'
    GROUP BY w.witness, p.companion, c.caretaker, o.owner, w.cat_name
    HAVING probability > 0 AND color_count > 0
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""


############### AGG ALL TESTS ##############
high_level_test_agg_all_1 = """
    SELECT cat_name, COUNT(*)
    FROM witnessed
    GROUP BY cat_name
    SHOW SENTENCE, PROBABILITY
"""

high_level_test_agg_all_2 = """
    SELECT cat_name, COUNT(*)
    FROM witnessed
    GROUP BY cat_name
    HAVING probability > 0
    SHOW SENTENCE, PROBABILITY
"""

# 7⚡
high_level_test_agg_all_3 = """
    SELECT cat_name, COUNT(*) as count_rows
    FROM witnessed
    WHERE cat_name = 'max'
    GROUP BY cat_name
    HAVING probability > 0 AND count_rows > 0
    SHOW SENTENCE, PROBABILITY
"""

high_level_test_agg_all_4 = """
    SELECT cat_name, COUNT(*) as count_rows
    FROM witnessed
    GROUP BY cat_name
    HAVING count_rows > 0
    SHOW PROBABILITY
"""

# NOTE: GROUP BY is still important to be present for the >1 table queries in particular! E.g., the following query:
# 7⚡
high_level_test_agg_all_5 = """
    SELECT w.cat_name, COUNT(*) as count_rows
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    WHERE p.color IN ('gray', 'black')
    GROUP BY w.cat_name
    HAVING count_rows > 0
    SHOW PROBABILITY
"""


########################################
############### RUN TESTS ##############
simple_high_level_tests = [high_level_test_simple_1, high_level_test_simple_2, high_level_test_simple_3, high_level_test_simple_4]
join_high_level_tests = [high_level_test_join_1, high_level_test_join_2, high_level_test_join_3, high_level_test_join_4, high_level_test_join_5, high_level_test_join_6, high_level_test_join_7, high_level_test_join_8]
order_limit_high_level_tests = [high_level_test_order_limit_1, high_level_test_order_limit_2]
mixed_data_high_level_tests = [high_level_test_mixed_data_1, high_level_test_mixed_data_2, high_level_test_mixed_data_3]
aggregation_high_level_tests = [high_level_test_agg_1, high_level_test_agg_2, high_level_test_agg_3, high_level_test_agg_4, high_level_test_agg_5, high_level_test_agg_6, high_level_test_agg_7]
distinct_high_level_tests = [high_level_test_distinct_1, high_level_test_distinct_2, high_level_test_distinct_3, high_level_test_distinct_4, high_level_test_distinct_5]
where_high_level_tests = [high_level_test_where_1, high_level_test_where_2]
where_having_high_level_tests = [high_level_test_where_having_1, high_level_test_where_having_2]
certain_data_high_level_tests = [high_level_test_certain_data_1, high_level_test_certain_data_2, high_level_test_certain_data_3]
large_query_high_level_tests = [high_level_test_large_query_1, high_level_test_large_query_2, high_level_test_large_query_3]
agg_all_result_high_level_tests = [high_level_test_agg_all_1, high_level_test_agg_all_2, high_level_test_agg_all_3, high_level_test_agg_all_4, high_level_test_agg_all_5]

# selected_high_level_tests = [high_level_test_agg_7]

high_level_tests = simple_high_level_tests + join_high_level_tests + order_limit_high_level_tests + mixed_data_high_level_tests + \
    aggregation_high_level_tests + distinct_high_level_tests + where_high_level_tests + where_having_high_level_tests + large_query_high_level_tests + agg_all_result_high_level_tests
# high_level_tests = selected_high_level_tests

def run_high_level_tests():
    for i, high_level_test in enumerate(high_level_tests):
        translated_layers = generate_full_translation(high_level_test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_high_level_tests()


high_level_tests = {
    "SIMPLE": [
        high_level_test_join_1,
        high_level_test_join_2,
    ],
    "JOIN + PROBABILITY": [
        high_level_test_join_3,
        high_level_test_join_8,
    ],
    "GROUP BY + AGGREGATE": [
        high_level_test_agg_1,
        high_level_test_agg_6,
    ],
    "DISTINCT": [
        high_level_test_distinct_2,
        high_level_test_distinct_4,
    ],
    "FILTERS": [
        high_level_test_where_1,
        high_level_test_where_having_1,
    ],
    "LARGE": [
        high_level_test_large_query_1,
        high_level_test_large_query_3,
    ],
    "COUNT(*)": [
        high_level_test_agg_all_3,
        high_level_test_agg_all_5,
    ],
    "MIXED DATA": [
        high_level_test_mixed_data_1,
        high_level_test_mixed_data_3,
    ]
}

high_level_test_names = [
    "high_level_test_join_1",
    "high_level_test_join_2",
    "high_level_test_join_3",
    "high_level_test_join_8",
    "high_level_test_agg_1",
    "high_level_test_agg_6",
    "high_level_test_distinct_2",
    "high_level_test_distinct_4",
    "high_level_test_where_1",
    "high_level_test_where_having_1",
    "high_level_test_large_query_1",
    "high_level_test_large_query_3",
    "high_level_test_agg_all_3",
    "high_level_test_agg_all_5",
    "high_level_test_mixed_data_1",
    "high_level_test_mixed_data_3"
]
