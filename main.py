import re
from typing import List, Tuple, Optional

""" TODO List (PostgreSQL + DuBio):
1. Support more complex queries:
    - Support for subqueries
    - Support for joins
    - Support for GROUP BY and HAVING clauses
    - Support for ORDER BY and LIMIT clauses
    - DISTINCT
    - conditioning

2. Extend the code with more complex DuBio features, such as:
    - Adding the | & operator for probabilistic joins
    - Adding other DuBio-specific functions like agg_or(), agg_and(), etc.

3. The current code expects syntactically correct SQL queries.

4. Handle certainty - when data is certain in a given table and there are no sentences

5. Add variables???
"""

# Extract the tables and their aliases **from** the **FROM** clause
# The regex looks for the pattern "FROM <table1> <alias1>, <table2> <alias2>, ..."
# The regex is case insensitive and allows for whitespace and newlines
# The regex uses non-capturing groups to ignore the WHERE clause and any trailing whitespace
# DOTALL - allow for newlines in the FROM clause
# IGNORECASE - make the search case insensitive
def extract_tables_from_from(sql: str) -> List[Tuple[str, str]]:
    from_match = re.search(
        r"FROM\s+(.+?)(?=\bWHERE\b|\bON\b|\bGROUP\b|\bORDER\b|\bLIMIT\b|;|$)",
        sql, re.IGNORECASE | re.DOTALL
    )
    if not from_match:
        return []
    from_clause = from_match.group(1)

    tables = []
    for part in from_clause.split(','):
        tokens = part.strip().split()
        if len(tokens) == 1:
            tables.append((tokens[0], tokens[0]))
        elif len(tokens) == 2:
            tables.append((tokens[0], tokens[1]))

    return tables


def extract_tables_from_joins(sql: str) -> List[Tuple[str, str]]:
    join_matches = re.findall(
        r"\bJOIN\s+(\w+)(?:\s+(\w+))?", sql, re.IGNORECASE
    )
    return [(table, alias if alias else table) for table, alias in join_matches]


def extract_all_tables(sql: str) -> List[Tuple[str, str]]:
    from_tables = extract_tables_from_from(sql)
    join_tables = extract_tables_from_joins(sql)

    # Set to avoid duplicates
    seen_aliases = set()
    all_tables = []
    for table, alias in from_tables + join_tables:
        if alias not in seen_aliases:
            all_tables.append((table, alias))
            seen_aliases.add(alias)

    return all_tables


# This function generates the sentence expression for the given aliases
def generate_sentence_expression(aliases: List[str]) -> str:
    return ' & '.join([f"{alias}._sentence" for alias in aliases])


# This function parses the SQL query to find the probability filter
# It looks for the WHERE clause and checks for a probability condition
# The regex looks for the pattern "probability <op> <value>" where <op> can be >, <, =, etc.
# and <value> is a number (with optional decimal)
def parse_probability_filter(sql: str) -> Optional[str]:
    match = re.search(r"WHERE\s+(.+)", sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    where_clause = match.group(1)
    prob_filter_match = re.search(r"(probability\s*[<>!=]+\s*(?:\d+\.\d+|\d+))", where_clause, re.IGNORECASE)
    return prob_filter_match.group(1) if prob_filter_match else None


def extract_select_from_clauses(sql: str) -> Tuple[Optional[str], Optional[str]]:
    select_match = re.search(r"SELECT\s+(.+?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
    from_match = re.search(r"FROM\s+(.+)", sql, re.IGNORECASE)
    select_clause = select_match.group(1).strip() if select_match else None
    from_clause = from_match.group(1).strip() if from_match else None
    return select_clause, from_clause


def generate_drop_views() -> str:
    return (
        "DROP VIEW IF EXISTS prob_view CASCADE;\n"
        "DROP VIEW IF EXISTS join_view CASCADE;"
    )


def generate_join_view(select_clause: str, from_clause: str, sentence_expr: str,
                       with_sentence: bool, needs_prob: bool) -> str:
    join_fields = select_clause
    if with_sentence or needs_prob:
        join_fields += f", {sentence_expr} AS _sentence"

    # Match compound JOIN types like FULL OUTER JOIN, preserving their full form
    formatted_from = re.sub(
        r"(\b(?:INNER|LEFT|RIGHT|FULL)(?:\s+OUTER)?|CROSS)\s+JOIN",
        lambda m: f"\n{m.group(0).upper()}",
        from_clause,
        flags=re.IGNORECASE
    )

    return (
        "CREATE OR REPLACE VIEW join_view AS\n"
        f"SELECT {join_fields}\n"
        f"FROM {formatted_from};"
    )


def generate_prob_view(dict_name: str) -> str:
    return (
        "CREATE OR REPLACE VIEW prob_view AS\n"
        "SELECT j.*, round(prob(d.dict, j._sentence)::numeric, 4) AS probability\n"
        "FROM join_view j, _dict d\n"
        f"WHERE d.name = '{dict_name}';"
    )


def generate_final_query(select_clause: str, with_prob: bool, with_sentence: bool,
                         prob_condition: Optional[str], needs_prob: bool) -> str:
    output_from = "prob_view" if needs_prob else "join_view"
    show_prob = "probability" if with_prob else ""
    show_sentence = "_sentence" if with_sentence else ""

    user_fields = [f.strip() for f in select_clause.split(",")]
    user_fields_as_alias = [
        re.split(r"\s+as\s+", field_alias, flags=re.IGNORECASE)[1].strip()
        if re.search(r"\s+as\s+", field_alias, flags=re.IGNORECASE)
        else field_alias.strip()
        for field_alias in user_fields
    ]
    fields_without_table_alias = [
        re.sub(r"^\w+\.", "", field_alias) for field_alias in user_fields_as_alias
    ]

    final_fields = fields_without_table_alias
    if show_prob:
        final_fields.append(show_prob)
    if show_sentence:
        final_fields.append(show_sentence)

    query = f"SELECT {', '.join(final_fields)}\nFROM {output_from}"
    if prob_condition:
        query += f"\nWHERE {prob_condition}"
    return query + ";"


def generate_full_translation(sql: str, dict_name: str = "mydict") -> List[str]:
    sql = sql.strip()
    with_prob = 'WITH PROBABILITY' in sql.upper()
    with_sentence = 'WITH SENTENCE' in sql.upper()
    sql = re.sub(r"\s+WITH PROBABILITY", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+WITH SENTENCE", "", sql, flags=re.IGNORECASE)

    prob_condition = parse_probability_filter(sql)
    needs_prob = with_prob or prob_condition is not None

    select_clause, from_clause = extract_select_from_clauses(sql)
    if not select_clause or not from_clause:
        return ["ERROR: Invalid SQL query format."]

    tables = extract_all_tables(sql)
    aliases = [alias for _, alias in tables]
    sentence_expr = generate_sentence_expression(aliases)

    view_queries = []
    view_queries.append(generate_drop_views())
    view_queries.append(generate_join_view(select_clause, from_clause, sentence_expr, with_sentence, needs_prob))

    if needs_prob:
        view_queries.append(generate_prob_view(dict_name))

    view_queries.append(generate_final_query(select_clause, with_prob, with_sentence, prob_condition, needs_prob))
    return view_queries


##### TESTING #####
test_1 = """
    SELECT d.person as suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car AND probability > 0.7
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
    WITH PROBABILITY
"""

test_4 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    WITH SENTENCE
"""

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

# RIGHT JOIN with WITH PROBABILITY
test_7 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s RIGHT JOIN drives d ON s.color = d.color AND s.car = d.car
    WITH PROBABILITY
"""

# FULL JOIN with WITH SENTENCE
test_8 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s FULL JOIN drives d ON s.color = d.color AND s.car = d.car
    WITH SENTENCE
"""

test_9 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s FULL OUTER JOIN drives d ON s.color = d.color AND s.car = d.car
    WITH PROBABILITY
"""

test_10 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s INNER JOIN drives d ON s.color = d.color AND s.car = d.car
    WITH SENTENCE
"""

test_11 = """
    SELECT d.person AS suspect, s.witness, s.color, s.car
    FROM saw s FULL INNER JOIN drives d ON s.color = d.color AND s.car = d.car FULL OUTER JOIN drives d ON s.color = d.color AND s.car = d.car
    WITH SENTENCE
"""


# Run the tests
tests = [test_1, test_2, test_3, test_4, test_5, test_6, test_7, test_8, test_9, test_10, test_11]

def run_tests():
    for i, test in enumerate(tests):
        translated_layers = generate_full_translation(test)
        print(f"\n\n---- TEST {i + 1} ----\n")
        print("\n\n".join(translated_layers))


if __name__ == "__main__":
    run_tests()
    # Uncomment the line below to test with a custom SQL query
    # print(generate_full_translation("SELECT * FROM table1 t1, table2 t2 WHERE t1.id = t2.id"))
