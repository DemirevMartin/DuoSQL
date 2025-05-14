import re
from typing import Tuple, List

""" TODO List:
1. Support more complex queries:
    - Support for subqueries
    - Support for different types of joins (INNER, LEFT, RIGHT, FULL)
    - Support for GROUP BY and HAVING clauses
    - Support for ORDER BY and LIMIT clauses
2. Ensure that PostgreSQL is fully supported
3. Extend the code with more complex DuBio features, such as:
    - Adding the | operator for probabilistic joins
    - Adding other DuBio-specific functions like agg_or(), agg_and(), etc.
"""


def extract_tables(sql: str) -> List[Tuple[str, str]]:
    """
    Extract table names and their aliases from the FROM clause
    Returns a list of (table_name, alias) tuples
    """
    from_match = re.search(r"FROM\s+(.+?)(?:\s+WHERE|\s*$)", sql, re.IGNORECASE | re.DOTALL)
    if not from_match:
        return []

    from_clause = from_match.group(1)
    tables = []
    for part in from_clause.split(','):
        tokens = part.strip().split()
        if len(tokens) == 1:
            tables.append((tokens[0], tokens[0]))  # table without alias
        elif len(tokens) == 2:
            tables.append((tokens[0], tokens[1]))  # table with alias
    return tables

def generate_sentence_expression(aliases: List[str]) -> str:
    """
    Generate _sentence expression using & operator for all aliases
    """
    return ' & '.join([f"{alias}._sentence" for alias in aliases])

def translate_general_query(user_sql: str, dict_name: str = "mydict") -> Tuple[str, bool]:
    """
    Generalized translation for any probabilistic SQL query to DuBio-compatible SQL
    """
    requires_dict = False
    original_sql = user_sql.strip()

    # Extract modifiers
    with_probability = 'WITH PROBABILITY' in original_sql.upper()
    with_sentence = 'WITH SENTENCE' in original_sql.upper()
    with_dictionary = 'WITH DICTIONARY' in original_sql.upper()

    # Remove custom clauses from input
    original_sql = re.sub(r"\s+WITH PROBABILITY", "", original_sql, flags=re.IGNORECASE)
    original_sql = re.sub(r"\s+WITH SENTENCE", "", original_sql, flags=re.IGNORECASE)
    original_sql = re.sub(r"\s+WITH DICTIONARY", "", original_sql, flags=re.IGNORECASE)

    # Extract SELECT and FROM
    select_match = re.search(r"SELECT\s+(.+?)\s+FROM", original_sql, re.IGNORECASE | re.DOTALL)
    from_clause_match = re.search(r"FROM\s+(.+)", original_sql, re.IGNORECASE)

    if not select_match or not from_clause_match:
        return "ERROR: Invalid SQL query format.", False

    select_clause = select_match.group(1).strip()
    from_clause = from_clause_match.group(1).strip()

    # Identify tables and aliases
    tables = extract_tables(original_sql)
    aliases = [alias for _, alias in tables]

    # Add _sentence propagation
    sentence_expr = generate_sentence_expression(aliases)
    new_fields = []

    if with_sentence or with_probability or with_dictionary:
        new_fields.append(f"{sentence_expr} AS _sentence")

    if with_probability:
        requires_dict = True
        new_fields.append(f"round(prob(d.dict, {sentence_expr})::numeric, 4) AS probability")

    if with_dictionary:
        requires_dict = True
        dict_expr = ' || '.join([f"{alias}._dictionary" for alias in aliases])
        new_fields.append(f"{dict_expr} AS _dictionary")

    if new_fields:
        select_clause += ", " + ", ".join(new_fields)

    # Handle _dict table join
    if requires_dict and '_dict' not in from_clause.lower():
        from_clause += ", _dict d"
        if 'WHERE' in original_sql.upper():
            translated_sql = re.sub(r"(WHERE\s+)", f"\\1d.name = '{dict_name}' AND ", original_sql, flags=re.IGNORECASE)
        else:
            translated_sql = original_sql + f" WHERE d.name = '{dict_name}'"
    else:
        translated_sql = original_sql

    # Replace old SELECT with new SELECT
    translated_sql = re.sub(r"SELECT\s+(.+?)\s+FROM", f"SELECT {select_clause} FROM", translated_sql, flags=re.IGNORECASE | re.DOTALL)

    return translated_sql, requires_dict


############# TESTS #############
user_input_general = """
    SELECT x.name, y.region
    FROM locations x, sightings y
    WHERE x.id = y.loc_id
    WITH PROBABILITY
"""

input2 = """
    SELECT d.person AS suspect, s.witness
    FROM saw s, drives d
    WHERE s.color = d.color AND s.car = d.car
    WITH SENTENCE
"""

translated_sql_gen, uses_dict_gen = translate_general_query(user_input_general)
print(translated_sql_gen)
print(f"Uses dictionary: {uses_dict_gen}")


translated_sql_gen, uses_dict_gen = translate_general_query(input2)
print("\nTranslated SQL for input2:")
print(translated_sql_gen)
print(f"Uses dictionary: {uses_dict_gen}")
