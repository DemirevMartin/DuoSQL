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

# -- INNER JOIN with SHOW SENTENCE (people who cared for cats that were also witnessed)
test_10 = """
    SELECT w.witness, c.caretaker AS person, w.cat_name, w.color
    FROM witnessed w INNER JOIN cares c
    ON w.cat_name = c.cat_name AND w.breed = c.breed
    SHOW SENTENCE
"""

# -- Complex joins with SHOW SENTENCE (cats that were witnessed, played with, and cared for)
test_11 = """
    SELECT w.witness, p.companion, c.caretaker, w.cat_name
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name
    FULL OUTER JOIN cares c ON w.cat_name = c.cat_name
    SHOW SENTENCE
"""

############## ORDER BY and LIMIT ##############
test_12 = """
    SELECT p.companion AS person, w.witness, w.cat_name, w.color
    FROM witnessed w
    INNER JOIN plays p ON w.cat_name = p.cat_name AND w.color = p.color
    WHERE probability > 0.7
    ORDER BY w.witness DESC, probability ASC
    LIMIT 10
    SHOW SENTENCE
"""

test_13 = """
    SELECT w.witness, p.companion AS person, w.cat_name, w.color
    FROM witnessed w
    LEFT OUTER JOIN plays p ON w.cat_name = p.cat_name AND w.breed = p.breed
    WHERE probability > 0.7
    ORDER BY probability DESC, w.witness ASC
    LIMIT 5
    SHOW PROBABILITY
"""

############### UN/CERTAIN Data ##############
test_14 = """
    SELECT w.witness, pc.cat_id, w.cat_name, w.color, w.breed
    FROM witnessed w
    JOIN profile_certain pc ON w.cat_name = pc.cat_name
    WHERE probability > 0.5
    ORDER BY pc.cat_id;
"""

test_15 = """
    SELECT p.companion, pc.cat_id, p.cat_name, p.color
    FROM plays p
    JOIN profile_certain pc ON p.cat_name = pc.cat_name
    SHOW PROBABILITY
    LIMIT 10;
"""

test_16 = """
    SELECT c.caretaker, pc.cat_id, c.cat_name, c.breed, c.age
    FROM cares c
    JOIN profile_certain pc ON c.cat_name = pc.cat_name
    SHOW SENTENCE;
"""


########################################
############### RUN TESTS ##############
simple_tests = [test_1, test_2, test_3, test_4]
join_tests = [test_5, test_6, test_7, test_8, test_9, test_10, test_11]
order_limit_tests = [test_12, test_13]
certain_data_tests = [test_14, test_15, test_16]

selected_tests = [test_6, test_7, test_8]

tests = certain_data_tests

def run_tests():
    for i, test in enumerate(tests):
        translated_layers = generate_full_translation(test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_tests()
