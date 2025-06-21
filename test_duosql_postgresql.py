# This script allows you to write a DuoSQL (high-level) query 
# and immediately receive both the translated SQL query and the results from the PostgreSQL.

import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from main import generate_full_translation

load_dotenv(".env")

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
database = os.getenv("DATABASE")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")


def run_high_level_query(query_str):
    sql_query = generate_full_translation(query_str)
    print('\n ------------ TRANSLATED SQL ------------ \n')
    sql_query = "\n\n".join(sql_query)
    print(sql_query)

    df = pd.read_sql_query(sql_query, engine)
    print('\n ------------ QUERY RESULTS ------------ \n')
    print(df)


if __name__ == "__main__":
    high_level_query = """
        SELECT w.witness, p.companion AS player, count(w.color) AS color_count
        FROM witnessed w
        JOIN plays p ON w.cat_name = p.cat_name
        WHERE w.cat_name = 'max'
        GROUP BY w.witness, p.companion, w.cat_name
        HAVING probability > 0 AND color_count > 0
        ORDER BY w.witness DESC, probability ASC
        LIMIT 10
        SHOW SENTENCE, PROBABILITY
    """
    run_high_level_query(high_level_query)
    engine.dispose()
