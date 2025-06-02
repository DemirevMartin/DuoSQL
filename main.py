"""TODO
    - Add counting rows (e.g., COUNT(*)), similar to the last function in aggregates.sql?
    - Include JOINs in the aggregate query
    - Ensure that everything works for (totally) certain data (different process)
"""
"""
    - Joining sentences - only '&'?
    - DISTINCT and aggregation - only 'agg_or()' for traversing all worlds?
    - If the probability of a row is 0, should it be excluded?
    - conditioning - what was it about?
"""
import re, os
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

############ CONSTANTS ############
# Load environment variables from .env file
load_dotenv(".env")

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
database = os.getenv("DATABASE")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")

REGEX_BOUNDING_CLAUSES: dict[str, str] = {
    "SELECT": r"\b(?=FROM|;|$)\b",
    "FROM_JOIN": r"\b(?=SHOW|GROUP|HAVING|ORDER|LIMIT|WHERE|;|$)\b",  # JOIN handled inside FROM
    "FROM_NO_JOIN": r"\b(?=JOIN|WHERE|GROUP|HAVING|ORDER|LIMIT|SHOW|;|$)\b",
    "WHERE": r"\b(?=GROUP|HAVING|ORDER|LIMIT|SHOW|;|$)\b",
    "GROUP": r"\b(?=HAVING|ORDER|LIMIT|SHOW|;|$)\b",
    "HAVING": r"\b(?=ORDER|LIMIT|SHOW|;|$)\b",
    "ORDER": r"\b(?=LIMIT|SHOW|;|$)\b",
    "LIMIT": r"\b(?=SHOW|;|$)\b"
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
    "SHOW": rf"\bSHOW\s+(.+?)"
}

REGEX_JOIN_CLAUSE_START: str = r"\b(?:(?:(?:LEFT|RIGHT|FULL)(?:\s+OUTER)?|INNER|CROSS)?\s*JOIN)\b"
REGEX_JOIN_CLAUSE: str = rf"{REGEX_JOIN_CLAUSE_START}\s+(\w+)(?:\s+(\w+))?"


########### SQL CLAUSE EXTRACTION ##########
# Checks SQL query correctness
def extract_select_from_clauses(sql: str) -> Tuple[Optional[str], Optional[str]]:
    select_match = re.search(REGEX_CLAUSE_STRUCTURES['SELECT'], sql, re.IGNORECASE | re.DOTALL)
    # NOTE: Essential to include the JOIN so it can be processed later
    from_match = re.search(REGEX_CLAUSE_STRUCTURES['FROM_JOIN'], sql, re.IGNORECASE | re.DOTALL)

    select_clause = select_match.group(1).strip() if select_match else None
    from_clause = from_match.group(1).strip() if from_match else None
    return select_clause, from_clause


def parse_where_clause(sql: str) -> Optional[str]:
    match = re.search(REGEX_CLAUSE_STRUCTURES['WHERE'], sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    raw_where = match.group(1).strip()

    # Remove table aliases like t1.field → field
    cleaned_where = re.sub(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.(?=[a-zA-Z_])", "", raw_where)
    return cleaned_where


def extract_order_by_and_limit(sql: str) -> Tuple[Optional[str], Optional[str]]:
    order_by = None
    limit = None

    # ORDER BY
    order_by_match = re.search(REGEX_CLAUSE_STRUCTURES['ORDER'], sql, re.IGNORECASE | re.DOTALL)
    if order_by_match:
        order_by = order_by_match.group(1).strip()
        # NOTE: Remove table aliases (if any!) - everything belongs to the view and has no alias anymore
        order_by = [re.sub(r"^\w+\.", "", part.strip()) for part in order_by.split(',')]
        order_by = ', '.join(order_by)

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


########## AGGREGATION ##########
def is_aggregate_query(sql: str) -> bool:
    return bool(re.search(r"\b(count|sum|avg|min|max)\s*\(", sql, re.IGNORECASE | re.DOTALL))


def extract_aggregate_query_parts(sql: str) -> Dict[str, Optional[str]]:
    sql = sql.strip().rstrip(';') + ';'  # normalize
    parts = {}

    for clause, pattern in REGEX_CLAUSE_STRUCTURES.items():
        match = re.search(pattern, sql, re.IGNORECASE | re.DOTALL)
        if match:
            parts[clause.lower()] = match.group(1).strip()
        else:
            parts[clause.lower()] = None

    return parts

########### DISTINCT ###########
def uses_distinct(sql: str) -> bool:
    return bool(re.match(r"\bSELECT\s+DISTINCT\b", sql, re.IGNORECASE))


######### PROBABILISTIC HANDLING ##########
def get_tables_with_sentence_column(tables: List[str]) -> Dict[str, bool]:
    """
    Checks if each table in the list has a `_sentence` column.
    Returns a dictionary: {table_name: True/False}
    """
    tables_with_sentence_column = []
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
            if has_sentence:
                tables_with_sentence_column.append(table)
    return tables_with_sentence_column


def generate_sentence_expression(tables: List[Tuple[str, str]], ) -> str:
    table_names = [tbl for tbl, _ in tables]
    tables_with_sentence_column = get_tables_with_sentence_column(table_names)
    
    if not tables_with_sentence_column:
        return None
    
    # NOTE: As handled in the extract_all_tables, all tables have an alias 
    # - whether they are specified in the SQL query or not.
    included_aliases = [
        alias for table, alias in tables
        if table in tables_with_sentence_column
    ]
    
    return ' & '.join([f"{alias}._sentence" for alias in included_aliases])


def requests_probability(sql: str) -> bool:
    return bool(re.search(r"\bprobability\b", sql, re.IGNORECASE | re.DOTALL))


########## VIEW CREATION ##########

def generate_drop_views() -> str:
    return (
        "DROP VIEW IF EXISTS prob_view CASCADE;\n"
        "DROP VIEW IF EXISTS join_view CASCADE;\n"
        "DROP VIEW IF EXISTS agg_view CASCADE;"
    )


def generate_join_view(select_clause: str, from_clause: str,
                       sentence_expression: str, needs_sentence: bool,
                       use_distinct: bool = False) -> str:

    # If DISTINCT and needs_sentence, group and use agg_or
    if use_distinct:
        # Parse SELECT fields for GROUP BY
        select_clause = re.sub(r"\s*DISTINCT\s*", "", select_clause, flags=re.IGNORECASE | re.DOTALL).strip()
        select_fields = [f.strip() for f in select_clause.split(",")]
        fields_without_aliases = [
            re.split(r"\s+as\s+", f, flags=re.IGNORECASE | re.DOTALL)[-1].strip() for f in select_fields
        ]

        join_fields = ", ".join(fields_without_aliases)
        group_by = ", ".join(fields_without_aliases)
        select_block = f"{join_fields}, agg_or(_sentence) AS _sentence"
        return (
            "CREATE OR REPLACE VIEW join_view AS\n"
            f"SELECT {select_block}\n"
            f"FROM {from_clause}\n"
            f"GROUP BY {group_by};"
        )

    join_fields = select_clause
    if sentence_expression and needs_sentence:
        join_fields += f", {sentence_expression} AS _sentence"

    from_clause = re.sub(r"[\s\t]+", " ", from_clause.strip(), flags=re.IGNORECASE | re.DOTALL)

    formatted_from = re.sub(
        REGEX_JOIN_CLAUSE_START,
        lambda m: f"\n{m.group(0).upper().strip()}",
        from_clause,
        flags=re.IGNORECASE | re.DOTALL
    )

    return (
        "CREATE OR REPLACE VIEW join_view AS\n"
        f"SELECT {join_fields}\n"
        f"FROM {formatted_from};"
    )


def generate_prob_view(view: str, dict_name: str) -> str:
    return (
        "CREATE OR REPLACE VIEW prob_view AS\n"
        "SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability\n"
        f"FROM {view} v, _dict d\n"
        f"WHERE d.name = '{dict_name}';"
    )


def build_aggregate_view(table: str, group_cols: list[str], agg_func: str, agg_field: str, alias: str = "agg_view") -> str:
    """
    Build an SQL view to compute probabilistic aggregates.
    :param table: The table name (e.g., 'witnessed')
    :param group_cols: List of columns to group by (e.g., ['cat_name'])
    :param agg_func: Aggregate function: 'count', 'sum', 'avg', 'min', 'max'
    :param agg_field: Field to aggregate (e.g., 'age')
    :param alias: Name for the final view
    """
    agg_func = agg_func.lower()
    bdd_func = f"prob_Bdd_{agg_func}"
    group_by = ", ".join(group_cols)
    arr = f"array_agg({agg_field})"
    arr_sentence = "array_agg(_sentence)"
    mask_gen = "generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::int)::bit(32)"

    return f"""CREATE OR REPLACE VIEW {alias} AS
SELECT {group_by}, {agg_func}, agg_or(_sentence) AS _sentence
FROM (
    SELECT {group_by}, {bdd_func}(arr,mask) AS {agg_func}, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT {group_by}, arr, arr_sentence, {mask_gen} AS mask
        FROM (
            SELECT {group_by}, {arr} arr, {arr_sentence} arr_sentence
            FROM (
                SELECT {group_by}, {agg_field}, agg_or(_sentence) AS _sentence
                FROM {table}
                GROUP BY {group_by}, {agg_field}
            ) AS first
            GROUP BY {group_by}
        ) AS second
    ) AS third
) AS forth
GROUP BY {group_by}, {agg_func};"""


########## FINAL QUERY CREATION ##########
def generate_final_query(select_clause: str, with_prob: bool, with_sentence: bool,
                         needs_prob: bool, where: Optional[str], 
                         order_by: Optional[str], limit: Optional[str]) -> str:
    output_from = "prob_view" if needs_prob else "join_view"
    show_probability = "probability" if with_prob else ""
    show_sentence = "_sentence" if with_sentence else ""

    user_fields = [f.strip() for f in select_clause.split(",")]
    user_fields_as_alias = [
        re.split(r"\s+as\s+", field_alias, flags=re.IGNORECASE | re.DOTALL)[1].strip()
        if re.search(r"\s+as\s+", field_alias, flags=re.IGNORECASE | re.DOTALL)
        else field_alias.strip()
        for field_alias in user_fields
    ]
    fields_without_table_alias = [
        re.sub(r"^\w+\.", "", field_alias) for field_alias in user_fields_as_alias
    ]

    final_fields = fields_without_table_alias
    if show_probability:
        final_fields.append(show_probability)
    if show_sentence:
        final_fields.append(show_sentence)

    query = f"SELECT {', '.join(final_fields)}\nFROM {output_from}"

    if where:
        query += f"\nWHERE {where}"
    if order_by:
        query += f"\nORDER BY {order_by}"
    if limit:
        query += f"\nLIMIT {limit}"

    return query + ";"


def generate_aggregate_query(sql, select_clause: str,
                            with_prob: bool = False, with_sentence: bool = False,
                            needs_prob: bool = False, 
                            where: Optional[str] = None, order_by: Optional[str] = None,
                            limit: Optional[str] = None, dict_name: str = "mydict") -> List[str]:
    
    parts = extract_aggregate_query_parts(sql)
    group_by = parts.get("group")
    having = parts.get("having")
    table = extract_all_tables(sql)[0][0]  # assume one table for now

    # Parse aggregation function and target from SELECT
    match = re.search(r"\b(count|sum|avg|min|max)\s*\(\s*(\*|\w+)\s*\)(?:\s+AS\s+(\w+)\b)?", select_clause, re.IGNORECASE | re.DOTALL)
    if not match:
        return ["ERROR: Unsupported or malformed aggregation."]
    agg_func, agg_target, alias = match.groups()
    agg_target = "1" if agg_target == "*" else agg_target
    
    # Handle alias presence
    original_agg_field = f"{agg_func}({agg_target}) AS {alias}" if alias else f"{agg_func}({agg_target})"
    final_agg_field = f"{agg_func} AS {alias}" if alias else f"{agg_func}"
    having = having.replace(original_agg_field, final_agg_field) if having else None

    # Build the aggregate view
    view_queries = []
    view_queries.append(generate_drop_views())
    view_queries.append(build_aggregate_view(table, [group_by], agg_func, agg_target, alias="agg_view"))

    if needs_prob:
        view_queries.append(generate_prob_view("agg_view", dict_name))

    final_output_table = "prob_view" if needs_prob else "agg_view"
    final_fields = [group_by, final_agg_field]
    if with_prob:
        final_fields.append("probability")
    if with_sentence:
        final_fields.append("_sentence")

    query = f"SELECT {', '.join(final_fields)}\nFROM {final_output_table}"

    if where or having:
        where = where if where else ""
        having = having if having else ""
        where_clause = f"{where} AND {having}" if where and having \
                        else f"{where}" if where else f"{having}"
        query += f"\nWHERE {where_clause}"

    if order_by:
        query += f"\nORDER BY {order_by}"
    if limit:
        query += f"\nLIMIT {limit}"

    view_queries.append(query + ";")
    return view_queries


def generate_full_translation(sql: str, dict_name: str = "mydict") -> List[str]:
    # User sql query input
    sql = sql.strip()

    # Extract SELECT and FROM clauses
    select_clause, from_clause = extract_select_from_clauses(sql)
    if not select_clause or not from_clause: # If the SQL query is not valid, return an error message
        return ["ERROR: Invalid SQL query format."]
    use_distinct = uses_distinct(sql)
    
    # NOTE: This is to solely SHOW the probability <=> different than 'needs_prob'!
    with_prob = re.search(r"\bSHOW\s+(.+)?\bPROBABILITY", sql.upper(), re.IGNORECASE | re.DOTALL) 
    with_sentence = re.search(r"\bSHOW\s+(.+)?\bSENTENCE", sql.upper(), re.IGNORECASE | re.DOTALL)

    # Check if there is a probability condition
    # NOTE: If SHOW PROBABILITY is not requested, we do not show the probability
    needs_prob = requests_probability(sql)
    needs_sentence = with_sentence is not None or needs_prob

    where = parse_where_clause(sql)
    # Extract ORDER BY and LIMIT clauses
    order_by, limit = extract_order_by_and_limit(sql)

    # Extract all tables and their aliases
    tables = extract_all_tables(sql)
    sentence_expression = generate_sentence_expression(tables)

    # Check for aggregate query
    if is_aggregate_query(sql):
        return generate_aggregate_query(
            sql, select_clause,
            with_prob=with_prob is not None,
            with_sentence=needs_sentence,
            needs_prob=needs_prob,
            where=where,
            order_by=order_by,
            limit=limit,
            dict_name=dict_name
        )

    view_queries = []
    view_queries.append(generate_drop_views())
    view_queries.append(generate_join_view(
        select_clause, from_clause, sentence_expression, 
        needs_sentence, use_distinct
    ))

    if needs_prob:
        view_queries.append(generate_prob_view("join_view", dict_name))

    final_query = generate_final_query(
        select_clause,
        with_prob,
        with_sentence,
        needs_prob,
        where,
        order_by,
        limit
    )
    final_query = re.sub(r"\s*DISTINCT\s*", " ", final_query, flags=re.IGNORECASE | re.DOTALL)  # Remove DISTINCT from the final query
    view_queries.append(final_query)
    return view_queries
