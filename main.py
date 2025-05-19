import re
from typing import List, Tuple, Optional

""" TODO List (PostgreSQL + DuBio):
1. Support more complex queries:
    - Support for subqueries
    - Support for joins
    - Support for GROUP BY and HAVING clauses
    - Support for ORDER BY and LIMIT clauses

2. Extend the code with more complex DuBio features, such as:
    - Adding the | operator for probabilistic joins
    - Adding other DuBio-specific functions like agg_or(), agg_and(), etc.
        -- Does my implementation really have to support them?

3. Take dict table name as input?

4. The current code expects syntactically correct SQL queries.
"""

# This function is used to extract the tables and their aliases from the SQL query
# The regex looks for the pattern "FROM <table1> <alias1>, <table2> <alias2>, ..."
# The regex is case insensitive and allows for whitespace and newlines
# The regex uses non-capturing groups to ignore the WHERE clause and any trailing whitespace
# DOTALL - allow for newlines in the FROM clause
# IGNORECASE - make the search case insensitive
def extract_tables(sql: str) -> List[Tuple[str, str]]:
    from_match = re.search(r"FROM\s+(.+?)(?:\s+WHERE|\s*$)", sql, re.IGNORECASE | re.DOTALL)
    if not from_match:
        return []
    from_clause = from_match.group(1)

    tables = []
    for part in from_clause.split(','):
        tokens = part.strip().split()  # E.g., when you have "FROM table1 t1, table2 t2" - the aliases are 't1' and 't2'
        if len(tokens) == 1:  # table without alias
            tables.append((tokens[0], tokens[0]))
        elif len(tokens) == 2:  # table with alias
            tables.append((tokens[0], tokens[1]))

    return tables


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


def generate_full_translation(sql: str, dict_name: str = "mydict") -> List[str]:
    sql = sql.strip()
    with_prob = 'WITH PROBABILITY' in sql.upper()
    with_sentence = 'WITH SENTENCE' in sql.upper()
    sql = re.sub(r"\s+WITH PROBABILITY", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+WITH SENTENCE", "", sql, flags=re.IGNORECASE)

    prob_condition = parse_probability_filter(sql)
    needs_prob = with_prob or prob_condition is not None

    select_match = re.search(r"SELECT\s+(.+?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
    from_match = re.search(r"FROM\s+(.+)", sql, re.IGNORECASE)

    if not select_match or not from_match:
        return ["ERROR: Invalid SQL query format."]

    select_clause = select_match.group(1).strip()
    from_clause = from_match.group(1).strip()

    tables = extract_tables(sql)
    aliases = [alias for _, alias in tables]
    sentence_expr = generate_sentence_expression(aliases)

    view_queries = []

    # 1. Join view
    join_fields = select_clause
    if with_sentence or needs_prob:
        join_fields += f", {sentence_expr} AS _sentence"

    join_view = (
        "CREATE OR REPLACE VIEW join_view AS\n"
        f"SELECT {join_fields}\n"
        f"FROM {from_clause};"
    )
    view_queries.append(join_view)

    # 2. Probability view
    if needs_prob:
        prob_view = (
            "CREATE OR REPLACE VIEW prob_view AS\n"
            "SELECT j.*, round(prob(d.dict, j._sentence)::numeric, 4) AS probability\n"
            "FROM join_view j, _dict d\n"
            f"WHERE d.name = '{dict_name}';"
        )
        view_queries.append(prob_view)

    # 3. Final query
    output_from = "prob_view" if needs_prob else "join_view"
    show_prob = "probability" if with_prob else ""
    show_sentence = "_sentence" if with_sentence else ""

    user_fields = [f.strip() for f in select_clause.split(",")]
    # If there is a field alias, get only it instead of the whole field_alias
    user_fields_as_alias = [
        # The regex ensures case insensitivity and requires spaces around 'as'
        re.split(r"\s+as\s+", field_alias, flags=re.IGNORECASE)[1].strip()
        if re.search(r"\s+as\s+", field_alias, flags=re.IGNORECASE)
        else field_alias.strip()
        for field_alias in user_fields
    ]
    fields_without_table_alias = [
        re.sub(r"^\w+\.", "", field_alias) for field_alias in user_fields_as_alias
    ]
    final_fields = fields_without_table_alias + ([show_prob] if show_prob else []) \
            + ([show_sentence] if show_sentence else [])
    final_fields = [f for f in final_fields if f or f == ""]  # remove empty

    final_query = f"SELECT {', '.join(final_fields)}\nFROM {output_from}"
    if prob_condition:
        final_query += f"\nWHERE {prob_condition}"
    final_query += ";"
    view_queries.append(final_query)

    return view_queries


##### TESTING #####
test_1 = """
    SELECT d.person as suspect, s.witness
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car AND probability > 0.7
"""

test_2 = """
    SELECT d.person AS suspect, s.witness
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
"""

test_3 = """
    SELECT d.person AS suspect, s.witness
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    WITH PROBABILITY
"""

test_4 = """
    SELECT d.person AS suspect, s.witness
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    WITH SENTENCE
"""


translated_layers = generate_full_translation(test_1)
print("\n---- RESULT 1 ----\n")
print("\n\n".join(translated_layers))

translated_layers = generate_full_translation(test_2)
print("\n\n---- RESULT 2 ----\n")
print("\n\n".join(translated_layers))

translated_layers = generate_full_translation(test_3)
print("\n\n---- RESULT 3 ----\n")
print("\n\n".join(translated_layers))

translated_layers = generate_full_translation(test_4)
print("\n\n---- RESULT 4 ----\n")
print("\n\n".join(translated_layers))

