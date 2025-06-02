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
test_certain_data_1 = """
    SELECT w.witness, pc.cat_id, w.cat_name, w.color, w.breed
    FROM witnessed w
    JOIN profile_certain pc ON w.cat_name = pc.cat_name
    WHERE probability > 0.5
    ORDER BY pc.cat_id;
"""

test_certain_data_2 = """
    SELECT p.companion, pc.cat_id, p.cat_name, p.color
    FROM plays p
    JOIN profile_certain pc ON p.cat_name = pc.cat_name
    SHOW PROBABILITY
    LIMIT 10;
"""

test_certain_data_3 = """
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


########################################
############### RUN TESTS ##############
simple_tests = [test_simple_1, test_simple_2, test_simple_3, test_simple_4]
join_tests = [test_join_1, test_join_2, test_join_3, test_join_4, test_join_5, test_join_6, test_join_7]
order_limit_tests = [test_order_limit_1, test_order_limit_2]
certain_data_tests = [test_certain_data_1, test_certain_data_2, test_certain_data_3]
aggregation_tests = [test_agg_1]
distinct_tests = [test_distinct_1, test_distinct_2]

selected_tests = [test_agg_1]

tests = distinct_tests

def run_tests():
    for i, test in enumerate(tests):
        translated_layers = generate_full_translation(test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_tests()
