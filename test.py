from main import generate_full_translation

############## SIMPLE TESTS ##############
test_simple_1 = """
    SELECT p.companion AS suspect, witness, w.color, w.cat_name
    FROM witnessed w, plays p
    WHERE w.color = p.color AND w.cat_name = p.cat_name
    HAVING probability > 0.1
    SHOW SENTENCE, PROBABILITY
"""

# Basic join with no extras 1⚡
test_simple_2 = """ 
    SELECT p.companion AS suspect, witness, w.color, w.cat_name
    FROM witnessed w, plays p
    WHERE w.color = p.color AND w.cat_name = p.cat_name
"""

# Same join, showing probabilities
test_simple_3 = """
    select p.companion as suspect, witness, w.color, w.cat_name
    from witnessed w, plays p
    where w.color = p.color and w.cat_name = p.cat_name
    show probability
"""

# Same join, showing sentence
test_simple_4 = """
    SELECT p.companion AS suspect, witness, w.color, w.cat_name
    FROM witnessed w, plays p
    WHERE w.color = p.color AND w.cat_name = p.cat_name
    SHOW SENTENCE
"""


############## JOIN ##############
# 1⚡
test_join_1 = """
    SELECT plays.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    JOIN plays
    ON w.cat_name = plays.cat_name AND w.color = plays.color AND w.breed = plays.breed
"""

# -- LEFT JOIN with aliases and no probability clause (see all witnessed cats and who possibly played with them)
test_join_2 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    LEFT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
    SHOW PROBABILITY
"""

# 2⚡
# -- RIGHT JOIN with SHOW PROBABILITY (see who played with a cat and whether they were witnessed)
test_join_3 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    RIGHT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
    SHOW PROBABILITY
"""

# -- FULL JOIN with SHOW SENTENCE (join all cats that were witnessed or played with, and show derivation)
test_join_4 = """
    SELECT w.witness, p.companion AS person, w.cat_name
    FROM witnessed w 
    FULL JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color
    SHOW SENTENCE
"""

# -- FULL OUTER JOIN with SHOW PROBABILITY (like above, but show probabilities)
test_join_5 = """
    SELECT w.witness, p.companion AS person, p.cat_name
    FROM witnessed w FULL OUTER JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color
    SHOW PROBABILITY
"""

# -- INNER JOIN with SHOW SENTENCE (people who cared for cats that were also witnessed)
test_join_6 = """
    SELECT w.witness, c.caretaker AS person, w.cat_name, w.color
    FROM witnessed w INNER JOIN cares c
    ON w.cat_name = c.cat_name AND w.breed = c.breed
    SHOW SENTENCE
"""

# -- Complex joins with SHOW SENTENCE (cats that were witnessed, played with, and cared for)
test_join_7 = """
    SELECT w.witness, p.companion AS player, c.caretaker, w.cat_name
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name
    FULL OUTER JOIN cares c ON w.cat_name = c.cat_name
    SHOW SENTENCE
"""

# 2 ⚡
test_join_8 = """
    SELECT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    JOIN cares c ON w.cat_name = c.cat_name
    JOIN owns o ON w.cat_name = o.cat_name
    SHOW SENTENCE, PROBABILITY
"""

############## ORDER BY and LIMIT ##############
test_order_limit_1 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    HAVING probability > 0.5
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE
"""

test_order_limit_2 = """
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
test_mixed_data_1 = """
    SELECT w.witness, pc.cat_id, w.cat_name, w.color, w.breed
    FROM witnessed w
    JOIN profile_certain pc ON w.cat_name = pc.cat_name
    HAVING probability > 0.5
    ORDER BY pc.cat_id;
"""

test_mixed_data_2 = """
    SELECT p.companion, pc.cat_id, p.cat_name, p.color
    FROM plays p
    JOIN profile_certain pc ON p.cat_name = pc.cat_name
    SHOW PROBABILITY
    LIMIT 10;
    
"""

# 8⚡
test_mixed_data_3 = """
    SELECT c.caretaker, pc.cat_id, c.cat_name, c.breed, c.age
    FROM cares c
    JOIN profile_certain pc ON c.cat_name = pc.cat_name
    JOIN owns o ON c.cat_name = o.cat_name
    SHOW SENTENCE;
"""

############## AGGREGATION ##############
# TODO Test sum, min, max, avg
# 3⚡
test_agg_1 = """
    SELECT cat_name, avg(age)
    FROM witnessed
    GROUP BY cat_name
    HAVING avg(age) > 2
    ORDER BY cat_name
    LIMIT 10
    SHOW PROBABILITY
"""

# Multiple GROUP BY
test_agg_2 = """
    SELECT cat_name, breed, avg(age)
    FROM witnessed
    GROUP BY cat_name, breed
    HAVING avg(age) > 2
    ORDER BY cat_name
    LIMIT 10
    SHOW PROBABILITY
"""

test_agg_5 = """
    SELECT w.cat_name, count(companion)
    FROM plays p, witnessed w
    WHERE w.cat_name = p.cat_name
    GROUP BY w.cat_name
    ORDER BY w.cat_name
    SHOW SENTENCE, PROBABILITY
"""

# 3⚡
test_agg_6 = """
    SELECT w.cat_name, count(companion)
    FROM plays p
    JOIN witnessed w ON w.cat_name = p.cat_name
    WHERE w.color = p.color
    GROUP BY w.cat_name
    ORDER BY w.cat_name
    SHOW SENTENCE, PROBABILITY
"""

############## DISTINCT ##############
test_distinct_1 = """
    SELECT DISTINCT breed
    FROM witnessed;
"""

# 4⚡
test_distinct_2 = """
    SELECT DISTINCT color
    FROM plays
    HAVING probability > 0.5
    ORDER BY color;
"""

test_distinct_3 = """
    SELECT DISTINCT p.age
    FROM plays p, witnessed w
    WHERE w.cat_name = p.cat_name
    HAVING probability > 0.5
    ORDER BY p.age;
"""

# 4⚡
test_distinct_4 = """ 
    SELECT DISTINCT p.age
    FROM plays p
    JOIN witnessed w ON w.cat_name = p.cat_name
    HAVING probability > 0.5
    ORDER BY p.age;
"""

test_distinct_5 = """
    SELECT DISTINCT w.witness, p.companion AS player, c.caretaker, o.owner, w.cat_name
    FROM witnessed w
    JOIN plays p ON w.cat_name = p.cat_name
    JOIN cares c ON w.cat_name = c.cat_name
    JOIN owns o ON w.cat_name = o.cat_name
    SHOW SENTENCE, PROBABILITY
"""

############### WHERE and HAVING ##############
# 5⚡
test_where_1 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    WHERE w.cat_name = 'max' AND w.color = 'gray'
    HAVING probability >= 0.25
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

test_where_2 = """
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
test_where_having_1 = """
    SELECT cat_name, COUNT(color)
    FROM witnessed
    WHERE color IN ('white', 'black')
    GROUP BY cat_name
    HAVING COUNT(color) > 0 AND probability > 0
    ORDER BY probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

test_where_having_2 = """
    SELECT cat_name, avg(age)
    FROM witnessed
    GROUP BY cat_name
    HAVING avg(age) > 2 AND probability > 0
    ORDER BY cat_name
    SHOW PROBABILITY
"""


############ CERTAIN DATA TESTS ##############
test_certain_data_1 = """
    SELECT *
    FROM profile_certain pc
"""

test_certain_data_2 = """
    SELECT pc.cat_id, pc.cat_name
    FROM profile_certain pc
    WHERE pc.cat_name = 'max'
    ORDER BY pc.cat_name
    SHOW SENTENCE, PROBABILITY
"""

# Triggers an error which is expected behavior
test_certain_data_3 = """
    SELECT pc.cat_id, pc.cat_name
    FROM profile_certain pc
    WHERE pc.cat_name = 'max'
    HAVING probability > 0.5 
    ORDER BY pc.cat_name
    SHOW SENTENCE, PROBABILITY
"""

############### LARGE QUERY TESTS ##############
# 6⚡
test_large_query_1 = """
    SELECT w.witness, plays.companion AS player, c.caretaker, o.owner, w.cat_name
    FROM witnessed w
    JOIN plays ON w.cat_name = plays.cat_name
    JOIN cares c ON w.cat_name = c.cat_name
    JOIN owns o ON w.cat_name = o.cat_name
    WHERE w.cat_name = 'max' AND w.color = 'gray'
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

test_large_query_2 = """
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
test_large_query_3 = """
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


############### ONE-CELL RESULT QUERY TESTS ##############
test_one_cell_1 = """
    SELECT cat_name, COUNT(*)
    FROM witnessed
    GROUP BY cat_name
    SHOW SENTENCE, PROBABILITY
"""

test_one_cell_2 = """
    SELECT cat_name, COUNT(*)
    FROM witnessed
    GROUP BY cat_name
    HAVING probability > 0
    SHOW SENTENCE, PROBABILITY
"""

# 7⚡
test_one_cell_3 = """
    SELECT cat_name, COUNT(*) as count_rows
    FROM witnessed
    WHERE cat_name = 'max'
    GROUP BY cat_name
    HAVING probability > 0 AND count_rows > 0
    SHOW SENTENCE, PROBABILITY
"""

test_one_cell_4 = """
    SELECT cat_name, COUNT(*) as count_rows
    FROM witnessed
    GROUP BY cat_name
    HAVING count_rows > 0
    SHOW PROBABILITY
"""

# NOTE: GROUP BY is still important to be present for the >1 table queries in particular! E.g., the following query:
test_one_cell_5 = """
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
simple_tests = [test_simple_1, test_simple_2, test_simple_3, test_simple_4]
join_tests = [test_join_1, test_join_2, test_join_3, test_join_4, test_join_5, test_join_6, test_join_7, test_join_8]
order_limit_tests = [test_order_limit_1, test_order_limit_2]
mixed_data_tests = [test_mixed_data_1, test_mixed_data_2, test_mixed_data_3]
aggregation_tests = [test_agg_1, test_agg_2, test_agg_5, test_agg_6]
distinct_tests = [test_distinct_1, test_distinct_2, test_distinct_3, test_distinct_4, test_distinct_5]
where_tests = [test_where_1, test_where_2]
where_having_tests = [test_where_having_1, test_where_having_2]
certain_data_tests = [test_certain_data_1, test_certain_data_2, test_certain_data_3]
large_query_tests = [test_large_query_1, test_large_query_2, test_large_query_3]
one_cell_result_tests = [test_one_cell_1, test_one_cell_2, test_one_cell_3, test_one_cell_4, test_one_cell_5]

selected_tests = [test_large_query_1]

# tests = simple_tests + join_tests + order_limit_tests + mixed_data_tests + \
#     aggregation_tests + distinct_tests + where_tests + where_having_tests + large_query_tests + one_cell_result_tests
tests = selected_tests

def run_tests():
    for i, test in enumerate(tests):
        translated_layers = generate_full_translation(test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_tests()
