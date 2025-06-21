import re, os
from typing import List, Tuple, Optional, Dict
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

############ CONSTANTS ############
# Load environment variables from .env file first
load_dotenv(".env")

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
database = os.getenv("DATABASE")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")

REGEX_BOUNDING_CLAUSES: dict[str, str] = {
    "SELECT": r"\b(?=FROM|;|$)\b",
    "FROM_JOIN": r"\b(?=SHOW|GROUP|HAVING|ORDER|LIMIT|WHERE|;|$)\b",  # JOIN handled inside FROM
    "FROM_NO_JOIN": r"\b(?:(?:JOIN|LEFT|RIGHT|INNER|CROSS)|WHERE|GROUP|HAVING|ORDER|LIMIT|SHOW|;|$)\b",
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
    "WHERE": rf"\bWHERE\s+(.+?){REGEX_BOUNDING_CLAUSES['WHERE']}",
    "GROUP": rf"\bGROUP\s+BY\s+(.+?){REGEX_BOUNDING_CLAUSES['GROUP']}",
    "HAVING": rf"\bHAVING\s+(.+?){REGEX_BOUNDING_CLAUSES['HAVING']}",
    "ORDER": rf"\bORDER\s+BY\s+(.+?){REGEX_BOUNDING_CLAUSES['ORDER']}",
    "LIMIT": rf"\bLIMIT\s+(.+?){REGEX_BOUNDING_CLAUSES['LIMIT']}",
    "SHOW": rf"\bSHOW\s+(.+?)"
}

REGEX_JOIN_CLAUSE_START: str = r"\b(?:(?:(?:LEFT|RIGHT|FULL)(?:\s+OUTER)?|INNER|CROSS)?\s*JOIN)\b"
REGEX_JOIN_CLAUSE: str = rf"{REGEX_JOIN_CLAUSE_START}\s+(\w+)(?:\s+(\w+))?\b\s*ON\b"


########### SQL CLAUSE EXTRACTION ##########
# For SELECT and FROM clauses extraction and query correctness checking
def extract_select_from_clauses(sql: str) -> Tuple[Optional[str], Optional[str]]:
    select_match = re.search(REGEX_CLAUSE_STRUCTURES['SELECT'], sql, re.IGNORECASE | re.DOTALL)
    # NOTE: Essential to include the JOIN so it can be processed later
    from_match = re.search(REGEX_CLAUSE_STRUCTURES['FROM_JOIN'], sql, re.IGNORECASE | re.DOTALL)

    select_clause = select_match.group(1).strip() if select_match else None
    from_clause = from_match.group(1).strip() if from_match else None
    return select_clause, from_clause


def remove_table_aliases(clause: str) -> str:
    """
    Removes table aliases from any clause. Excludes cases like 2.00 and similar (e.g., present in the WHERE clause)
    Example: "t1.field AS field" → "field"; "a.field > 2.00" → "field > 2.00"
    """
    cleaned_clause = re.sub(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.(?=[a-zA-Z_])", "", clause)
    return cleaned_clause.strip()


# Parse the WHERE clause from the SQL query
def parse_where_clause(sql: str) -> Optional[str]:
    match = re.search(REGEX_CLAUSE_STRUCTURES['WHERE'], sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    raw_where = match.group(1).strip()
    return raw_where


# Extract ORDER BY and LIMIT clauses from the SQL query
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

# Extract the tables and their aliases from the FROM clause
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
        tokens = re.split(r'\s+', part.strip())
        if len(tokens) == 1:
            tables.append((tokens[0], tokens[0]))
        elif len(tokens) == 2:
            tables.append((tokens[0], tokens[1]))

    return tables


# Extract the tables and their aliases from the JOIN clauses
def extract_tables_from_joins(sql: str) -> List[Tuple[str, str]]:
    # NOTE: We focus only on the JOIN clauses, not the FROM clause
    join_matches = re.findall(REGEX_JOIN_CLAUSE, sql, re.IGNORECASE)
    return [(table, alias if alias else table) for table, alias in join_matches]


# Extract all tables and their aliases from the SQL query
def extract_all_tables(sql: str) -> List[Tuple[str, str]]:
    from_tables = extract_tables_from_from(sql)
    join_tables = extract_tables_from_joins(sql)

    # Utilize a set to avoid duplicates
    seen_aliases = set()
    all_tables = []
    for table, alias in from_tables + join_tables:
        if alias not in seen_aliases:
            all_tables.append((table, alias))
            seen_aliases.add(alias)

    return all_tables


########## AGGREGATION ##########
# Check if the SQL query is an aggregate query (containing COUNT, SUM, AVG, MIN, or MAX)
def is_aggregate_query(sql: str) -> bool:
    return bool(re.search(r"\b(count|sum|avg|min|max)\s*\(", sql, re.IGNORECASE | re.DOTALL))


# Check if the SQL query is an aggregate query that uses all rows (COUNT(*))
def is_aggregate_all_query(sql: str) -> bool:
    """
    Checks if the SQL query is an aggregate query that uses all rows (COUNT(*)).
    Returns True if it is, otherwise False.
    """
    return bool(re.search(r"\b(count|sum|avg|min|max)\s*\(\s*\*\s*\)", sql, re.IGNORECASE | re.DOTALL))


# This method iterates over all clauses (used only for aggregate queries)
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
# Check if the SQL query uses DISTINCT in the SELECT clause
def uses_distinct(sql: str) -> bool:
    return bool(re.match(r"\bSELECT\s+DISTINCT\b", sql, re.IGNORECASE))


######### PROBABILISTIC STRUCTURES HANDLING ##########
# Create a dictionary holding the tables and whether they have a `_sentence` column
def get_tables_with_sentence_column(tables: List[str]) -> Dict[str, bool]:
    """
    Checks if each table in the list has a `_sentence` column.
    Returns a dictionary: {table_name: True/False}
    """
    tables_with_sentence_column: dict[str, bool] = {}
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
                tables_with_sentence_column[table] = True
    return tables_with_sentence_column


# Check if any table in the provided dictionary has a `_sentence` column
def has_uncertainty(tables_with_sentence_column: Dict[str, bool]) -> bool:
    """
    Checks if any table in the provided dictionary has a `_sentence` column.
    Returns True if at least one table has it, otherwise False.
    """
    return any(tables_with_sentence_column.values())


# Generate the sentence expression for the SQL query
def generate_sentence_expression(tables: List[Tuple[str, str]]) -> str:
    table_names = [tbl for tbl, _ in tables]
    tables_with_sentence_column = get_tables_with_sentence_column(table_names)
    
    if not has_uncertainty(tables_with_sentence_column):
        return "certain"

    if not tables_with_sentence_column:
        return None
    
    # NOTE: As handled in the extract_all_tables, all tables have an alias 
    # - whether they are specified in the SQL query or not.
    included_aliases = [
        alias for table, alias in tables
        if table in tables_with_sentence_column
    ]
    
    return ' & '.join([f"{alias}._sentence" for alias in included_aliases])


# Check if the SQL query requests probability in the HAVING or the SHOW clause
def requests_probability(sql: str) -> bool:
    return bool(re.search(r"\bprobability\b", sql, re.IGNORECASE | re.DOTALL))


########## VIEW CREATION ##########
# The (relevant) views must be dropped before creating new ones 
# since they are correlated and even "CREATE OR REPLACE" is not enough to avoid errors
def generate_drop_views(prob: bool = False, join: bool = False, agg: bool = False, agg_all: bool = False) -> str:
    result = []
    if prob:
        result.append("DROP VIEW IF EXISTS prob_view CASCADE;")
    if join:
        result.append("DROP VIEW IF EXISTS join_view CASCADE;")
    if agg:
        result.append("DROP VIEW IF EXISTS agg_view CASCADE;")
    if agg_all:
        result.append("DROP VIEW IF EXISTS agg_all_view CASCADE;")

    return "\n".join(result)


# For non-aggregate queries
def generate_join_view(select_clause: str, from_clause: str, where_clause: str,
                       sentence_expression: str, with_sentence: bool, with_prob: bool, needs_prob: bool,
                       use_distinct: bool) -> str:
    """
    Generates an SQL view for the JOIN operation based on the provided clauses.
    Args:
        select_clause (str): The SELECT clause of the SQL query.
        from_clause (str): The FROM clause of the SQL query.
        where_clause (str): The WHERE clause of the SQL query.
        sentence_expression (str): The expression generated from the sentence columns.
        with_sentence (bool): Whether to include the _sentence column in the output.
        with_prob (bool): Whether to include the probability column in the output.
        needs_prob (bool): Whether the query requires probability calculation.
        use_distinct (bool): Whether to use DISTINCT in the SELECT clause.
    Returns:
        str: The SQL join_view creation statement.
    """

    # Clean and format the SELECT clause
    from_clause = re.sub(r"[\s\t]+", " ", from_clause.strip(), flags=re.IGNORECASE | re.DOTALL)
    formatted_from = re.sub(
        REGEX_JOIN_CLAUSE_START,
        lambda m: f"\n{m.group(0).upper().strip()}",
        from_clause,
        flags=re.IGNORECASE | re.DOTALL
    )
    where_clause = "" if not where_clause else f"\nWHERE {where_clause}"

    # DISTINCT handling
    if use_distinct:
        select_clause = re.sub(r"\s*DISTINCT\s*", "", select_clause, flags=re.IGNORECASE | re.DOTALL).strip()

        # Parse SELECT fields for GROUP BY
        select_fields = [f.strip() for f in select_clause.split(",")]
        fields_without_aliases = [
            re.split(r"\s+as\s+", f, flags=re.IGNORECASE | re.DOTALL)[-1].strip() for f in select_fields
        ]
        group_by = ", ".join(fields_without_aliases)

        select_clause += f", agg_or({sentence_expression}) AS _sentence"

        return (
            "CREATE OR REPLACE VIEW join_view AS"
            f"\nSELECT {select_clause}"
            f"\nFROM {formatted_from}"
            f"{where_clause}"
            f"\nGROUP BY {group_by};"
        )

    if with_sentence or with_prob or needs_prob:
        select_clause += f", {sentence_expression} AS _sentence"

    return (
        "CREATE OR REPLACE VIEW join_view AS"
        f"\nSELECT {select_clause}"
        f"\nFROM {formatted_from}"
        f"{where_clause};"
    )


# For probabilistic queries - generates a view that calculates the probability of each sentence (used in all queries)
def generate_prob_view(view: str, dict_name: str) -> str:
    return (
        "CREATE OR REPLACE VIEW prob_view AS\n"
        "SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability\n"
        f"FROM {view} v\n"
        f"JOIN _dict d ON d.name = '{dict_name}';"
    )


# For aggregate_all queries - COUNT(*)
def build_aggregate_all_view(from_clause: str,
                             group_col: str, where: str,
                             agg_func: str,
                             final_agg_name: str,
                             sentence_expression: str) -> str:
    """
    Builds an SQL view for aggregate ALL queries (e.g., COUNT(*)).
    Args:
        from_clause (str): The FROM clause of the SQL query.
        group_col (str): The column to group by.
        where (str): The WHERE clause of the SQL query.
        agg_func (str): The aggregation function to use (e.g., COUNT, SUM).
        final_agg_name (str): The correct form of the final aggregation field to be used in the view.
        sentence_expression (str): The expression generated from the sentence columns.
    Returns:
        str: The SQL aqg_all_view creation statement.
    """

    # Clean and format the FROM clause
    from_clause = re.sub(r"[\s\t]+", " ", from_clause.strip(), flags=re.IGNORECASE | re.DOTALL)
    formatted_from = re.sub(
        REGEX_JOIN_CLAUSE_START,
        lambda m: f"\n\t\t{m.group(0).upper().strip()}",
        from_clause,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Format all fields, structures, and functions for the view query
    agg_func = agg_func.lower()
    bdd_aggregation_func = f"prob_Bdd_{agg_func}"
    where = f"\n\t\tWHERE {where}" if where else ""
    inner_group_by = "" if '&' in sentence_expression else f"\n\t\tGROUP BY {group_col}"

    arr = f"array_agg({remove_table_aliases(group_col)})"
    inner_sentence = sentence_expression if '&' in sentence_expression else f"agg_or(_sentence)"
    arr_sentence = f"array_agg(_sentence)"
    mask_gen = "generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64)"

    return f"""CREATE OR REPLACE VIEW agg_all_view AS
SELECT {final_agg_name}, agg_or(_sentence) AS _sentence
FROM (
    SELECT {bdd_aggregation_func}(arr,mask) AS {final_agg_name}, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT arr, arr_sentence, {mask_gen} AS mask
        FROM (
            SELECT {arr} arr, {arr_sentence} AS arr_sentence
            FROM (
                SELECT {group_col}, {inner_sentence} AS _sentence
                FROM {formatted_from}{where}{inner_group_by}
            ) AS first
            GROUP BY TRUE
        ) AS second
    ) AS third
) AS forth
GROUP BY {final_agg_name};"""


# For aggregate queries (excluding COUNT(*))
def build_aggregate_view(from_clause: str, group_cols: list[str], 
                         agg_func, agg_target, final_agg_name: str, 
                         sentence_expression: str,
                         where: Optional[str]) -> str:
    """
    Builds an SQL view for aggregate queries (e.g., COUNT, SUM, AVG, MIN, MAX).
    Args:
        from_clause (str): The FROM clause of the SQL query.
        group_cols (list[str]): The columns to group by.
        agg_func (str): The aggregation function to use (e.g., COUNT, SUM).
        agg_target (str): The target column for aggregation.
        final_agg_name (str): The correct form of the final aggregation field to be used in the view.
        sentence_expression (str): The expression generated from the sentence columns.
        where (Optional[str]): The WHERE clause of the SQL query.
    Returns:
        str: The SQL agg_view creation statement.
    """

    # Clean and format the FROM clause
    from_clause = re.sub(r"[\s\t]+", " ", from_clause.strip(), flags=re.IGNORECASE | re.DOTALL)
    formatted_from = re.sub(
        REGEX_JOIN_CLAUSE_START,
        lambda m: f"\n\t\t{m.group(0).upper().strip()}",
        from_clause,
        flags=re.IGNORECASE | re.DOTALL
    )
    where = f"\n\t\tWHERE {where}" if where else ""

    # Format all fields, structures, and functions for the view query
    agg_func = agg_func.lower()
    bdd_aggregation_func = f"prob_Bdd_{agg_func}"
    group_by_no_aliases = remove_table_aliases(', '.join(group_cols)).strip()
    group_by = ", ".join(group_cols)

    inner_group_by_clauses = []
    inner_group_by_clauses.append("" if '&' in sentence_expression else f"\n\t\tGROUP BY {group_by}, {agg_target}")
    inner_group_by_clauses.append(f"GROUP BY {group_by_no_aliases}")

    arr = f"array_agg({remove_table_aliases(agg_target)})"
    inner_sentence = sentence_expression if '&' in sentence_expression else f"agg_or(_sentence)"
    arr_sentence = "array_agg(_sentence)"
    mask_gen = "generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::bigint)::bit(64)"

    return f"""CREATE OR REPLACE VIEW agg_view AS
SELECT {group_by_no_aliases}, {final_agg_name}, agg_or(_sentence) AS _sentence
FROM (
    SELECT {group_by_no_aliases}, {bdd_aggregation_func}(arr,mask) AS {final_agg_name}, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT {group_by_no_aliases}, arr, arr_sentence, {mask_gen} AS mask
        FROM (
            SELECT {group_by_no_aliases}, {arr} arr, {arr_sentence} arr_sentence
            FROM (
                SELECT {group_by}, {agg_target}, {inner_sentence} AS _sentence
                FROM {formatted_from}{where}{inner_group_by_clauses[0]}
            ) AS first
            {inner_group_by_clauses[1]}
        ) AS second
    ) AS third
) AS forth
GROUP BY {group_by_no_aliases}, {final_agg_name};"""


########## FINAL QUERY CREATION ##########
# Generates the final SQL query for non-aggregate queries
def generate_final_query(select_clause: str, with_prob: bool, with_sentence: bool,
                         needs_prob: bool, having: Optional[str],
                         order_by: Optional[str], limit: Optional[str]) -> str:
    """
    Generates the final SQL query based on the provided clauses and options.
    Args:
        select_clause (str): The SELECT clause of the SQL query.
        with_prob (bool): Whether to include the probability in the final query.
        with_sentence (bool): Whether to include the sentence in the final query.
        needs_prob (bool): Whether the query requires probability calculation.
        having (Optional[str]): The HAVING clause of the SQL query.
        order_by (Optional[str]): The ORDER BY clause of the SQL query.
        limit (Optional[str]): The LIMIT clause of the SQL query.
    Returns:
        str: The final SQL query.
    """

    # Clean and format the SELECT clause
    user_fields = [f.strip() for f in select_clause.split(",")]
    user_fields_as_alias = [
        re.split(r"\s+as\s+", field_alias, flags=re.IGNORECASE | re.DOTALL)[1].strip() # The [1] is the alias part
        if re.search(r"\s+as\s+", field_alias, flags=re.IGNORECASE | re.DOTALL)
        else field_alias.strip()
        for field_alias in user_fields
    ]
    fields_without_table_alias = remove_table_aliases(', '.join(user_fields_as_alias)).split(', ')

    final_fields = fields_without_table_alias
    if with_prob:
        final_fields.append("probability")
    if with_sentence:
        final_fields.append("_sentence")

    output_from = "prob_view" if needs_prob else "join_view"
    query = f"SELECT {', '.join(final_fields)}\nFROM {output_from}"

    if having:
        query += f"\nWHERE {having}"
    if order_by:
        query += f"\nORDER BY {order_by}"
    if limit:
        query += f"\nLIMIT {limit}"

    return query + ";"


# For aggregate_all queries - COUNT(*)
def generate_aggregate_all_query(select_clause: str, from_clause: str, where: str,
                                 group_by: str, having: str, order_by: str, limit: str,
                                 with_prob: bool = False, with_sentence: bool = False,
                                 sentence_expression: str = "certain",
                                 needs_prob: bool = False,
                                 dict_name: str = "cats_short") -> list[str]:
    """
    Generates the SQL query for aggregate ALL queries (COUNT(*)).
    Args:
        select_clause (str): The SELECT clause of the SQL query.
        from_clause (str): The FROM clause of the SQL query.
        where (str): The WHERE clause of the SQL query.
        group_by (str): The GROUP BY clause of the SQL query.
        having (str): The HAVING clause of the SQL query.
        order_by (str): The ORDER BY clause of the SQL query.
        limit (str): The LIMIT clause of the SQL query.
        with_prob (bool): Whether to include the probability in the final query.
        with_sentence (bool): Whether to include the sentence in the final query.
        sentence_expression (str): The expression generated from the sentence columns.
        needs_prob (bool): Whether the query requires probability calculation.
        dict_name (str): The name of the dictionary for probability calculation.
    Returns:
        list[str]: A list of SQL queries to create the necessary views and the final query.
    """

    # Parse aggregation function and target from SELECT
    match = re.search(r"\b(count|sum|avg|min|max)\s*\(\s*\*\s*\)(?:\s+AS\s+(\w+)\b)?", select_clause, re.IGNORECASE | re.DOTALL)
    if not match:
        return ["ERROR: Unsupported or malformed aggregation."]
    agg_func, alias = match.groups()
    final_agg_field = alias if alias else agg_func

    view_queries = []
    view_queries.append(generate_drop_views(prob=True, agg_all=True))
    view_queries.append(build_aggregate_all_view(
        from_clause, group_by, where, agg_func, final_agg_field, sentence_expression
    ))

    if needs_prob:
        view_queries.append(generate_prob_view("agg_all_view", dict_name))

    final_fields = [final_agg_field]
    if with_prob:
        final_fields.append("probability")
    if with_sentence:
        final_fields.append("_sentence")

    final_output_table = "prob_view" if needs_prob else "agg_all_view"
    query = f"SELECT {', '.join(final_fields)}\nFROM {final_output_table}"

    if having:
        query += f"\nWHERE {having}"
    if order_by:
        query += f"\nORDER BY {order_by}"
    if limit:
        query += f"\nLIMIT {limit}"

    view_queries.append(query + ";")
    return view_queries


# For aggregate queries (excluding COUNT(*))
def generate_aggregate_query(select_clause: str, from_clause: str,
                            group_by: str, having: str,
                            with_prob: bool = False, with_sentence: bool = False,
                            sentence_expression: str = "certain",
                            needs_prob: bool = False, 
                            where: Optional[str] = None, order_by: Optional[str] = None,
                            limit: Optional[str] = None, dict_name: str = "cats_short") -> List[str]:
    """
    Generates the SQL query for aggregate queries (e.g., COUNT, SUM, AVG, MIN, MAX).
    Args:
        select_clause (str): The SELECT clause of the SQL query.
        from_clause (str): The FROM clause of the SQL query.
        group_by (str): The GROUP BY clause of the SQL query.
        having (str): The HAVING clause of the SQL query.
        with_prob (bool): Whether to include the probability in the final query.
        with_sentence (bool): Whether to include the sentence in the final query.
        sentence_expression (str): The expression generated from the sentence columns.
        needs_prob (bool): Whether the query requires probability calculation.
        where (Optional[str]): The WHERE clause of the SQL query.
        order_by (Optional[str]): The ORDER BY clause of the SQL query.
        limit (Optional[str]): The LIMIT clause of the SQL query.
        dict_name (str): The name of the dictionary for probability calculation.
    Returns:
        List[str]: A list of SQL queries to create the necessary views and the final query.
    """

    # Parse aggregation function and target from SELECT
    match = re.search(r"\b(count|sum|avg|min|max)\s*\(\s*(\*|(?:\w+\.)?\w+)\s*\)(?:\s+AS\s+(\w+)\b)?", select_clause, re.IGNORECASE | re.DOTALL)
    if not match:
        return ["ERROR: Unsupported or malformed aggregation."]
    agg_func, agg_target, alias = match.groups()
    agg_target = "1" if agg_target == "*" else agg_target
    
    # Handle alias presence
    combined_agg_no_alias = f"{agg_func}({agg_target})"
    final_agg_field = alias if alias else agg_func
    having = having.replace(combined_agg_no_alias, final_agg_field) if having else None

    # Build the aggregate view
    view_queries = []
    view_queries.append(generate_drop_views(prob=True, agg=True))
    view_queries.append(build_aggregate_view(from_clause, [group_by], 
                                             agg_func, agg_target, final_agg_field, sentence_expression, where))

    if needs_prob:
        view_queries.append(generate_prob_view("agg_view", dict_name))

    final_fields = [group_by, final_agg_field]
    if with_prob:
        final_fields.append("probability")
    if with_sentence:
        final_fields.append("_sentence")

    # Clean the final fields from table aliases - join them since they must be a string, not a list
    final_fields = remove_table_aliases(', '.join(final_fields)).split(', ')
    final_output_table = "prob_view" if needs_prob else "agg_view"
    query = f"SELECT {', '.join(final_fields)}\nFROM {final_output_table}"

    if having: # Everything has been grouped and aggregated already, so we use WHERE instead of HAVING
        query += f"\nWHERE {having}"
    if order_by:
        query += f"\nORDER BY {order_by}"
    if limit:
        query += f"\nLIMIT {limit}"

    view_queries.append(query + ";")
    return view_queries


def generate_full_translation(sql: str, dict_name: str = "cats_short") -> List[str]:
    # User sql query input
    sql = sql.strip()

    # Extract SELECT and FROM clauses
    select_clause, from_clause = extract_select_from_clauses(sql)
    if not select_clause or not from_clause: # If the SQL query is not valid, return an informative error message
        return ["ERROR: Invalid SQL query format."]
    use_distinct = uses_distinct(sql)
    
    # NOTE: This is to solely SHOW the probability <=> different than 'needs_prob'!
    with_prob = re.search(r"\bSHOW\s+(.+)?\bPROBABILITY", sql.upper(), re.IGNORECASE | re.DOTALL)
    with_prob = with_prob is not None
    with_sentence = re.search(r"\bSHOW\s+(.+)?\bSENTENCE", sql.upper(), re.IGNORECASE | re.DOTALL)
    with_sentence = with_sentence is not None

    # Check if there is a probability condition in the HAVING clause
    # NOTE: If SHOW PROBABILITY is not requested, we do not show the probability
    needs_prob = requests_probability(sql)

    where = parse_where_clause(sql)
    order_by, limit = extract_order_by_and_limit(sql)

    # Extract the aggregate query parts for aggregate queries
    parts = extract_aggregate_query_parts(sql)
    group_by = parts.get("group")
    having = parts.get("having")

    # Extract all tables and their aliases
    tables = extract_all_tables(sql)
    # Generate the sentence expression based on the tables
    sentence_expression = generate_sentence_expression(tables)

    # Check if the data is completely certain
    if sentence_expression == "certain":
        if having and re.search(r"\bprobability\b", having, re.IGNORECASE | re.DOTALL): 
            return ["ERROR: Cannot show probability for completely certain data. Please remove the probability condition from the HAVING clause."]
        if with_prob or with_sentence:
            sql = re.sub(r"\bSHOW.*", "", sql, flags=re.IGNORECASE | re.DOTALL)
        return [sql]


    # Check for aggregate ALL query
    if is_aggregate_all_query(sql):
        # Finalize the process since it is an aggregate ALL query
        return generate_aggregate_all_query(
            select_clause,
            from_clause,
            where,
            group_by,
            having,
            order_by, 
            limit,
            with_prob=with_prob,
            with_sentence=with_sentence,
            sentence_expression=sentence_expression,
            needs_prob=needs_prob,
            dict_name=dict_name
        )

    # Check for aggregate query
    if is_aggregate_query(sql):
        # Finalize the process since it is an aggregate query
        return generate_aggregate_query(
            select_clause, from_clause, group_by, having,
            with_prob=with_prob,
            with_sentence=with_sentence,
            sentence_expression=sentence_expression,
            needs_prob=needs_prob,
            where=where,
            order_by=order_by,
            limit=limit,
            dict_name=dict_name
        )

    view_queries = []
    view_queries.append(generate_drop_views(prob=True, join=True))
    view_queries.append(generate_join_view(
        select_clause, from_clause, where, sentence_expression, 
        with_sentence, with_prob, needs_prob, use_distinct
    ))

    if needs_prob:
        view_queries.append(generate_prob_view("join_view", dict_name))

    final_query = generate_final_query(
        select_clause,
        with_prob,
        with_sentence,
        needs_prob,
        having,
        order_by,
        limit
    )
    final_query = re.sub(r"\s*DISTINCT\s*", " ", final_query, flags=re.IGNORECASE | re.DOTALL)  # Remove DISTINCT from the final query
    view_queries.append(final_query)
    return view_queries
