""" TODO List (PostgreSQL + DuBio):
1. Support more complex queries:
    - Support for JOINs ✅
    - Support for user VIEWs
    - Support for subqueries 
    - Support for ORDER BY and LIMIT clauses ✅
    - Support for GROUP BY and HAVING clauses
    - DISTINCT
    - conditioning

2. Handle certainty - when data is certain in a given table and there are no sentences ✅

3. Postgres Tests

4. Extend the code with more complex DuBio features, such as:
    - Adding the | & operator for probabilistic joins
    - Adding other DuBio-specific functions like agg_or(), agg_and(), etc.
"""
import re, os
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv(".env")

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
database = os.getenv("DATABASE")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")

############ CONSTANTS ############
REGEX_BOUNDING_CLAUSES: dict[str, str] = {
    "SELECT": r"\bFROM",
    "FROM_JOIN": r"\b(?:WHERE|GROUP|HAVING|ORDER|LIMIT|SHOW|;|$)", # NOTE: JOIN is not included here, as it is handled together with FROM
    "FROM_NO_JOIN": r"\b(?:JOIN|WHERE|GROUP|HAVING|ORDER|LIMIT|SHOW|;|$)", 
    "WHERE": r"\b(?:GROUP|HAVING|ORDER|LIMIT|SHOW|;|$)",
    "GROUP": r"\b(?:HAVING|ORDER|LIMIT|SHOW|;|$)",
    "HAVING": r"\b(?:ORDER|LIMIT|SHOW|;|$)",
    "ORDER": r"\b(?:LIMIT|SHOW|;|$)",
    "LIMIT": r"\b(?:SHOW|;|$)",
    "SHOW": r";|$"
}

REGEX_CLAUSE_STRUCTURES: dict[str, str] = {
    "SELECT": rf"\bSELECT\s+(.+?){REGEX_BOUNDING_CLAUSES['SELECT']}",
    "FROM_JOIN": rf"\bFROM\s+(.+?){REGEX_BOUNDING_CLAUSES['FROM_JOIN']}",
    "FROM_NO_JOIN": rf"\bFROM\s+(.+?){REGEX_BOUNDING_CLAUSES['FROM_NO_JOIN']}",
    "JOIN": rf"\bJOIN\s+(\w+)(?=\s+(\w+))?{REGEX_BOUNDING_CLAUSES['FROM_NO_JOIN']}",
    "WHERE": rf"\bWHERE\s+(.+?){REGEX_BOUNDING_CLAUSES['WHERE']}",
    "GROUP": rf"\bGROUP\s+BY\s+(.+?){REGEX_BOUNDING_CLAUSES['GROUP']}",
    "HAVING": rf"\bHAVING\s+(.+?){REGEX_BOUNDING_CLAUSES['HAVING']}",
    "ORDER": rf"\bORDER\s+BY\s+(.+?){REGEX_BOUNDING_CLAUSES['ORDER']}",
    "LIMIT": rf"\bLIMIT\s+(.+?){REGEX_BOUNDING_CLAUSES['LIMIT']}",
    "SHOW": rf"\bSHOW\s+(.+?){REGEX_BOUNDING_CLAUSES['SHOW']}"
}

REGEX_JOIN_CLAUSE_START: str = r"\b(?:(?:(?:LEFT|RIGHT|FULL)(?:\s+OUTER)?|INNER|CROSS)?\s*JOIN)\b"
REGEX_JOIN_CLAUSE: str = rf"{REGEX_JOIN_CLAUSE_START}\s+(\w+)(?:\s+(\w+))?"
REGEX_JOIN_KEYWORD_SEARCH: str = rf"(?<!\n)(?<!\n\s*){REGEX_JOIN_CLAUSE_START}"


########### SQL CLAUSE EXTRACTION ##########

# Checks SQL query correctness
def extract_select_from_clauses(sql: str) -> Tuple[Optional[str], Optional[str]]:
    select_match = re.search(REGEX_CLAUSE_STRUCTURES['SELECT'], sql, re.IGNORECASE | re.DOTALL)
    # NOTE: Essential to include the JOIN so it can be processed later
    from_match = re.search(REGEX_CLAUSE_STRUCTURES['FROM_JOIN'], sql, re.IGNORECASE | re.DOTALL)

    select_clause = select_match.group(1).strip() if select_match else None
    from_clause = from_match.group(1).strip() if from_match else None
    return select_clause, from_clause


def extract_order_by_and_limit(sql: str) -> Tuple[Optional[str], Optional[str]]:
    order_by = None
    limit = None

    # ORDER BY
    order_by_match = re.search(REGEX_CLAUSE_STRUCTURES['ORDER'], sql, re.IGNORECASE | re.DOTALL)
    if order_by_match:
        order_by = order_by_match.group(1).strip()

    # LIMIT
    limit_match = re.search(REGEX_CLAUSE_STRUCTURES['LIMIT'], sql, re.IGNORECASE | re.DOTALL)
    if limit_match:
        limit = limit_match.group(1).strip()

    return order_by, limit


########### TABLE EXTRACTION ##########

# Extract the tables and their aliases **from** the **FROM** clause
# The regex looks for the pattern "FROM <table1> <alias1>, <table2> <alias2>, ..."
# The regex is case insensitive and allows for whitespace and newlines
# The regex uses non-capturing groups to ignore the WHERE clause and any trailing whitespace
# DOTALL - allow for newlines in the FROM clause
# IGNORECASE - make the search case insensitive
def extract_tables_from_from(sql: str) -> List[Tuple[str, str]]:
    # NOTE: We focus only on the FROM clause without JOINs
    from_match = re.search(REGEX_CLAUSE_STRUCTURES['FROM_NO_JOIN'], sql, re.IGNORECASE | re.DOTALL)

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
    # NOTE: We focus only on the JOIN clauses, not the FROM clause
    join_matches = re.findall(REGEX_JOIN_CLAUSE, sql, re.IGNORECASE)
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


######### PROBABILISTIC HANDLING ##########

def get_tables_with_sentence_column(tables: List[str]) -> Dict[str, bool]:
    """
    Checks if each table in the list has a `_sentence` column.
    Returns a dictionary: {table_name: True/False}
    """
    result = {}
    with engine.connect() as conn:
        for table in set(tables):
            query = text("""
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = :table
                AND column_name = '_sentence'
                LIMIT 1
            """)
            has_sentence = conn.execute(query, {"table": table}).scalar() is not None
            result[table] = has_sentence
    return result


# NOTE: As handled in the extract_all_tables, all tables have an alias 
# - whether they are specified in the SQL query or not.
def generate_sentence_expression_conditional(tables: List[Tuple[str, str]]) -> str:
    """
    Only includes aliases for tables that have a `_sentence` column.
    """
    table_names = [tbl for tbl, _ in tables]
    sentence_map = get_tables_with_sentence_column(table_names)
    
    included_aliases = [
        alias for table, alias in tables
        if sentence_map.get(table, False)
    ]
    
    return ' & '.join([f"{alias}._sentence" for alias in included_aliases])


# This function parses the SQL query to find the probability filter
# It looks for the WHERE clause and checks for a probability condition
# The regex looks for the pattern "probability <op> <value>" where <op> can be >, <, =, etc.
# and <value> is a number (with optional decimal)
def parse_probability_filter(sql: str) -> Optional[str]:
    match = re.search(REGEX_CLAUSE_STRUCTURES['WHERE'], sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    where_clause = match.group(1)
    prob_filter_match = re.search(r"\b(probability\s*[<>!=]+\s*(?:\d+\.\d+|\d+))", where_clause, re.IGNORECASE)
    return prob_filter_match.group(1) if prob_filter_match else None


########## VIEW CREATION ##########

def generate_drop_views() -> str:
    return (
        "DROP VIEW IF EXISTS prob_view CASCADE;\n"
        "DROP VIEW IF EXISTS join_view CASCADE;"
    )


# join_regex_keyword = r"\b(((LEFT|RIGHT|FULL)(\s+OUTER)?|INNER|CROSS)?\s*JOIN)\b"
import re

def generate_join_view(select_clause: str, from_clause: str, sentence_expr: str,
                       with_sentence: bool, needs_prob: bool) -> str:
    join_fields = select_clause
    if with_sentence or needs_prob:
        join_fields += f", {sentence_expr} AS _sentence"

    # Insert newline before JOIN and uppercase it
    formatted_from = re.sub(
        REGEX_JOIN_KEYWORD_SEARCH,
        lambda m: f"\n{m.group(0).upper().strip()}",
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


########## FINAL QUERY CREATION ##########

def generate_final_query(select_clause: str, with_prob: bool, with_sentence: bool,
                         prob_condition: Optional[str], needs_prob: bool,
                         order_by: Optional[str], limit: Optional[str]) -> str:
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
    if order_by:
        query += f"\nORDER BY {order_by}"
    if limit:
        query += f"\nLIMIT {limit}"

    return query + ";"


def generate_full_translation(sql: str, dict_name: str = "mydict") -> List[str]:
    # User query input
    sql = sql.strip()
    with_prob = re.search(r"\bSHOW\s+(.+)?PROBABILITY", sql.upper())
    with_sentence = re.search(r"\bSHOW\s+(.+)?SENTENCE", sql.upper())
    sql = re.sub(r"SHOW\s+(.+)?", "", sql, flags=re.IGNORECASE)

    # Check if probability is requested
    prob_condition = parse_probability_filter(sql)
    needs_prob = with_prob or prob_condition is not None

    # Extract SELECT and FROM clauses
    select_clause, from_clause = extract_select_from_clauses(sql)
    if not select_clause or not from_clause: # If the SQL query is not valid, return an error message
        return ["ERROR: Invalid SQL query format."]
    
    # Extract ORDER BY and LIMIT clauses
    order_by, limit = extract_order_by_and_limit(sql)

    # Extract all tables and their aliases
    tables = extract_all_tables(sql)
    sentence_expr = generate_sentence_expression_conditional(tables)

    view_queries = []
    view_queries.append(generate_drop_views())
    view_queries.append(generate_join_view(select_clause, from_clause, sentence_expr, with_sentence, needs_prob))

    if needs_prob:
        view_queries.append(generate_prob_view(dict_name))

    view_queries.append(generate_final_query(
        select_clause,
        with_prob,
        with_sentence,
        prob_condition,
        needs_prob,
        order_by,
        limit
    ))
    return view_queries
