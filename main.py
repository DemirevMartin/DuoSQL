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

query = """
    SELECT d.person AS suspect, s.witness,
        s._sentence & d._sentence AS _sentence
    FROM pp2425_32.saw s, pp2425_32.drives d
    WHERE s.color = d.color
    AND s.car = d.car
"""

df = pd.read_sql_query(query, engine)

engine.dispose()

print(df)