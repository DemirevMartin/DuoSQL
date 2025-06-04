from main import generate_full_translation

############## SIMPLE TESTS ##############
test_simple_1 = """
    SELECT d.person as suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car AND probability > 0.7
    SHOW SENTENCE
"""

test_simple_2 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
"""

test_simple_3 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    SHOW PROBABILITY
"""

test_simple_4 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    SHOW SENTENCE
"""

############## JOIN ##############
# -- INNER JOIN with aliases and WHERE clause (find people who played with cats that were witnessed, with high certainty)
test_join_1 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    RIGHT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
"""

# -- LEFT JOIN with aliases and no probability clause (see all witnessed cats and who possibly played with them)
test_join_2 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    LEFT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
    SHOW PROBABILITY
"""

# -- RIGHT JOIN with SHOW PROBABILITY (see who played with a cat and whether they were witnessed)
test_join_3 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    LEFT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
    SHOW PROBABILITY
"""

# -- FULL JOIN with SHOW SENTENCE (join all cats that were witnessed or played with, and show derivation)
test_join_4 = """
    SELECT w.witness, p.companion AS person, w.cat_name AS cat_name
    FROM witnessed w 
    FULL JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color
    SHOW SENTENCE
"""

# -- FULL OUTER JOIN with SHOW PROBABILITY (like above, but show probabilities)
test_join_5 = """
    SELECT w.witness, p.companion AS person, p.cat_name AS cat_name
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
    SELECT w.witness, p.companion, c.caretaker, w.cat_name
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name
    FULL OUTER JOIN cares c ON w.cat_name = c.cat_name
    SHOW SENTENCE
"""

############## ORDER BY and LIMIT ##############
test_order_limit_1 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    WHERE probability > 0.7
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE
"""

test_order_limit_2 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    LEFT OUTER JOIN plays p ON w.cat_name = p.cat_name AND w.breed = p.breed
    WHERE probability > 0.7
    ORDER BY probability DESC, w.witness ASC
    LIMIT 5
    SHOW PROBABILITY
"""

############### UN/CERTAIN Data ##############
test_mixed_data_1 = """
    SELECT w.witness, pc.cat_id, w.cat_name, w.color, w.breed
    FROM witnessed w
    JOIN profile_certain pc ON w.cat_name = pc.cat_name
    WHERE probability > 0.5
    ORDER BY pc.cat_id;
"""

test_mixed_data_2 = """
    SELECT p.companion, pc.cat_id, p.cat_name, p.color
    FROM plays p
    JOIN profile_certain pc ON p.cat_name = pc.cat_name
    SHOW PROBABILITY
    LIMIT 10;
"""

test_mixed_data_3 = """
    SELECT c.caretaker, pc.cat_id, c.cat_name, c.breed, c.age
    FROM cares c
    JOIN profile_certain pc ON c.cat_name = pc.cat_name
    SHOW SENTENCE;
"""

############## AGGREGATION ##############
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

# Multiple aggregation
test_agg_3 = """
    SELECT cat_name, avg(age), count(color)
    FROM witnessed
    GROUP BY cat_name
    ORDER BY cat_name
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

# Multiple aggregation + GROUP BY with HAVING
test_agg_4 = """
    SELECT cat_name, breed, avg(age), count(color)
    FROM witnessed
    GROUP BY cat_name, breed
    HAVING avg(age) > 2 AND count(color) > 3
    ORDER BY cat_name
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

############## DISTINCT ##############
test_distinct_1 = """
    SELECT DISTINCT breed
    FROM witnessed;
"""

test_distinct_2 = """
    SELECT DISTINCT color
    FROM plays
    WHERE probability > 0.5
    ORDER BY color;
"""

############### WHERE (and HAVING) ##############
test_where_1 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    WHERE probability >= 0.25 AND w.cat_name = 'max' AND w.color = 'gray'
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

test_where_2 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    LEFT OUTER JOIN plays p ON w.cat_name = p.cat_name AND w.breed = p.breed
    WHERE probability > 0.3 AND w.cat_name = 'max' AND (w.color = 'gray' OR w.color = 'black')
    ORDER BY probability DESC, w.witness ASC
    LIMIT 5
    SHOW PROBABILITY
"""

test_where_having_1 = """
    SELECT cat_name, COUNT(color)
    FROM witnessed
    WHERE probability > 0
    GROUP BY cat_name
    HAVING COUNT(color) > 1
    ORDER BY probability ASC
    LIMIT 10
    SHOW SENTENCE, PROBABILITY
"""

test_where_having_2 = """
    SELECT cat_name, avg(age)
    FROM witnessed
    WHERE probability > 0
    GROUP BY cat_name
    HAVING avg(age) > 2
    ORDER BY cat_name
    SHOW PROBABILITY
"""


############ CERTAIN DATA TESTS ##############
test_certain_data_1 = """
    SELECT *
    FROM profile_certain pc
"""

test_certain_data_2 = """
    SELECT pc.cat_id, pc.cat_name, pc.color, pc.breed, pc.age
    FROM profile_certain pc
    WHERE pc.age > 2
    ORDER BY pc.cat_name
    SHOW SENTENCE
"""

########################################
############### RUN TESTS ##############
simple_tests = [test_simple_1, test_simple_2, test_simple_3, test_simple_4]
join_tests = [test_join_1, test_join_2, test_join_3, test_join_4, test_join_5, test_join_6, test_join_7]
order_limit_tests = [test_order_limit_1, test_order_limit_2]
mixed_data_tests = [test_mixed_data_1, test_mixed_data_2, test_mixed_data_3]
aggregation_tests = [test_agg_1, test_agg_2, test_agg_3, test_agg_4]
distinct_tests = [test_distinct_1, test_distinct_2]
where_tests = [test_where_1, test_where_2]
where_having_tests = [test_where_having_1, test_where_having_2]
certain_data_tests = [test_certain_data_1, test_certain_data_2]

selected_tests = [test_agg_3, test_agg_4]

tests = selected_tests

def run_tests():
    for i, test in enumerate(tests):
        translated_layers = generate_full_translation(test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_tests()
