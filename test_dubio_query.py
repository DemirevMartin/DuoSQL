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
    
engine.dispose()