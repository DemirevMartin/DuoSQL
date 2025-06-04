import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

load_dotenv(".env")

user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
database = os.getenv("DATABASE")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{database}")


def initial_dubio_test():
    query_where = f"""
        SELECT d.person AS suspect, s.witness,
            s._sentence & d._sentence AS _sentence
        FROM saw s, drives d
        WHERE s.color = d.color AND s.car = d.car
    """

    query_print_dict = f"""
        SELECT print(dict) FROM _dict WHERE name = 'mydict'
    """

    print('\n ---- QUERY 1 ----\n')
    df = pd.read_sql_query(query_where, engine)
    print(df)

    print('\n ---- QUERY 2 ----\n')
    df = pd.read_sql_query(query_print_dict, engine)

    for index, row in df.iterrows():
        print(f"Row {index}:")
        for column in df.columns:
            print(f"  {column}: {row[column]}")
        print()


def aggregation_test():
    query = """
DROP VIEW IF EXISTS prob_view CASCADE;
DROP VIEW IF EXISTS join_view CASCADE;
DROP VIEW IF EXISTS agg_view CASCADE;

CREATE OR REPLACE VIEW agg_view AS
SELECT cat_name, avg, agg_or(_sentence) AS _sentence
FROM (
    SELECT cat_name, prob_Bdd_avg(arr,mask) AS avg, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT cat_name, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::int)::bit(32) AS mask
        FROM (
            SELECT cat_name, array_agg(age) arr, array_agg(_sentence) arr_sentence
            FROM (
                SELECT cat_name, age, agg_or(_sentence) AS _sentence
                FROM witnessed
                GROUP BY cat_name, age
            ) AS first
            GROUP BY cat_name
        ) AS second
    ) AS third
) AS forth
GROUP BY cat_name, avg;

CREATE OR REPLACE VIEW prob_view AS
SELECT v.*, round(prob(d.dict, v._sentence)::numeric, 4) AS probability
FROM agg_view v, _dict d
WHERE d.name = 'mydict';

SELECT cat_name, avg, probability, _sentence
FROM prob_view
WHERE avg > 2
ORDER BY cat_name
LIMIT 10;"""

    print('\n ---- AGGREGATION ----\n')
    result = pd.read_sql_query(query, engine)
    print(result)

if __name__ == "__main__":
    aggregation_test()
    engine.dispose()
    