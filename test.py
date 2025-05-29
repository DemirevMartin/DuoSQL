from main import generate_full_translation

############## SIMPLE TESTS ##############
test_1 = """
    SELECT d.person as suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car AND probability > 0.7
    SHOW SENTENCE
"""

test_2 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
"""

test_3 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    SHOW PROBABILITY
"""

test_4 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    SHOW SENTENCE
"""

############## JOIN ##############

# -- INNER JOIN with aliases and WHERE clause (find people who played with cats that were witnessed, with high certainty)
test_5 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    RIGHT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
"""

# -- LEFT JOIN with aliases and no probability clause (see all witnessed cats and who possibly played with them)
test_6 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    LEFT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
    SHOW PROBABILITY
"""

# -- RIGHT JOIN with SHOW PROBABILITY (see who played with a cat and whether they were witnessed)
test_7 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color, w.breed
    FROM witnessed w
    LEFT JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color AND w.breed = p.breed
    SHOW PROBABILITY
"""

# -- FULL JOIN with SHOW SENTENCE (join all cats that were witnessed or played with, and show derivation)
test_8 = """
    SELECT w.witness, p.companion AS person, w.cat_name AS cat_name
    FROM witnessed w 
    FULL JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color
    SHOW SENTENCE
"""

# -- FULL OUTER JOIN with SHOW PROBABILITY (like above, but show probabilities)
test_9 = """
    SELECT w.witness, p.companion AS person, p.cat_name AS cat_name
    FROM witnessed w FULL OUTER JOIN plays p
    ON w.cat_name = p.cat_name AND w.color = p.color
    SHOW PROBABILITY
"""


########################################
############### RUN TESTS ##############
simple_tests = [test_1, test_2, test_3, test_4]
# join_tests = [test_5, test_6, test_7, test_8, test_9, test_10, test_11]
# order_limit_tests = [test_12, test_13]
# view_tests = [test_14]

# certain_data_tests = [test_15, test_16, test_17]

selected_tests = [test_6, test_7, test_8]

tests = selected_tests

def run_tests():
    for i, test in enumerate(tests):
        translated_layers = generate_full_translation(test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_tests()
    # Uncomment the line below to test with a custom SQL query
    # print(generate_full_translation("SELECT * FROM table1 t1, table2 t2 WHERE t1.id = t2.id"))
