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
    FROM saw s, drives d, 
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

# INNER JOIN with aliases and WHERE clause
test_5 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s INNER JOIN drives d ON s.color = d.color AND s.car = d.car
    WHERE probability > 0.7
"""

# LEFT JOIN with aliases and no probability
test_6 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s LEFT JOIN drives d ON s.color = d.color AND s.car = d.car
"""

# RIGHT JOIN with SHOW PROBABILITY
test_7 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s RIGHT JOIN drives d ON s.color = d.color AND s.car = d.car
    SHOW PROBABILITY
"""

# FULL JOIN with SHOW SENTENCE
test_8 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s FULL JOIN drives d ON s.color = d.color AND s.car = d.car
    SHOW SENTENCE
"""

test_9 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s FULL OUTER JOIN drives d ON s.color = d.color AND s.car = d.car
    SHOW PROBABILITY
"""

test_10 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s INNER JOIN drives d ON s.color = d.color AND s.car = d.car
    SHOW SENTENCE
"""

test_11 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s FULL INNER JOIN drives d ON s.color = d.color AND s.car = d.car FULL OUTER JOIN drives d ON s.color = d.color AND s.car = d.car
    SHOW SENTENCE
"""

############## ORDER BY and LIMIT ##############
test_12 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s 
    INNER JOIN drives d ON s.color = d.color AND s.car = d.car
    WHERE probability > 0.7
    ORDER BY s.witness DESC
    LIMIT 10
"""

test_13 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s 
    LEFT OUTER JOIN drives d ON s.color = d.color AND s.car = d.car
    WHERE probability > 0.7
    ORDER BY s.witness DESC
    LIMIT 5
    SHOW PROBABILITY
"""

############## user-defined VIEWs ##############
test_14 = """
    CREATE VIEW v1 AS
    SELECT * FROM saw
    SHOW SENTENCE;

    CREATE VIEW v2 AS
    SELECT * FROM v1
    SHOW PROBABILITY;

    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM v1 s, v2 d
    WHERE s.color = d.color AND s.car = d.car
"""

############### UN/CERTAIN Data ##############
test_15 = """
    SELECT p.person, c.car
    FROM drives_certain d
    FULL JOIN person_certain p ON d.person_id = p.id
    RIGHT JOIN car_certain c ON d.car_id = c.id
    JOIN car_certain c ON d.car_id = c.id
    RIGHT OUTER JOIN car_certain c ON d.car_id = c.id
    LEFT JOIN car_certain c ON d.car_id = c.id;
"""

test_16 = """
    SELECT p.person
    FROM saw_certain
    JOIN person_certain p ON saw_certain.person_id = p.id
    JOIN car_certain c ON saw_certain.car_id = c.id
    WHERE c.color = 'red';
"""

test_17 = """
    SELECT p.person
    FROM drives_certain d
    JOIN person_certain p ON d.person_id = p.id
    INNER JOIN car_certain c ON d.car_id = c.id
    WHERE c.color = 'black' AND c.car = 'Tesla';
"""

test_18 = """
    SELECT observer.person AS observer, owner.person AS owner
    FROM saw_certain s
    JOIN person_certain observer ON s.person_id = observer.id
    JOIN drives_certain d ON s.car_id = d.car_id
    JOIN person_certain owner ON d.person_id = owner.id;
"""

test_19 = """   
    SELECT p.person
    FROM saw_certain s
    JOIN person_certain p ON s.person_id = p.id
    JOIN drives_certain d ON d.person_id = p.id
    WHERE s.car_id = d.car_id;
"""

# Combining certain and uncertain data
test_20 = """
    SELECT p.person, c.car
    FROM drives_certain d JOIN person_certain p ON d.person_id = p.id
    JOIN car_certain c ON d.car_id = c.id
    WHERE p.person IN (SELECT person FROM drives_uncertain);
"""

########################################
############### RUN TESTS ##############
simple_tests = [test_1, test_2, test_3, test_4]
join_tests = [test_5, test_6, test_7, test_8, test_9, test_10, test_11]
order_limit_tests = [test_12, test_13]
# view_tests = [test_14]

certain_data_tests = [test_15, test_16, test_17, test_18, test_19, test_20]

tests = certain_data_tests

def run_tests():
    for i, test in enumerate(tests):
        translated_layers = generate_full_translation(test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_tests()
    # Uncomment the line below to test with a custom SQL query
    # print(generate_full_translation("SELECT * FROM table1 t1, table2 t2 WHERE t1.id = t2.id"))
