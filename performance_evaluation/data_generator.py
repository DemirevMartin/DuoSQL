import random

names = ["alice", "ben", "cathy", "david", "emma", "frank", "grace", "henry", "irene", "jack"]
cat_names = ["luna", "max", "bella", "oreo", "tiger", "milo"]
breeds = ["siamese", "tabby", "mainecoon", "persian", "ragdoll", "sphynx"]
colors = ["white", "gray", "black", "orange"]
ages = list(range(1, 16))

# Function to generate dictionary insert SQL
def generate_dict_insert(table_prefix: str, count: int) -> str:
    entries = []
    for i in range(1, count + 1):
        entries.append(f"{table_prefix}{i}=1:0.5;     {table_prefix}{i}=2:0.5")
    joined = "\n".join(entries)
    return f"\n{joined}"

# Function to generate SQL inserts
def generate_insert_statements(table_name: str, prefix: str, count: int) -> str:
    statements = []
    for i in range(1, count + 1):
        id_val = i
        person = random.choice(names)
        cat = random.choice(cat_names)
        breed = random.choice(breeds)
        color = random.choice(colors)
        age = random.choice(ages)
        sentence_value = random.choice([1, 2])
        sentence = f"{prefix}{i}={sentence_value}"
        bdd = f"Bdd('{sentence}')"
        stmt = f"({id_val},'{person}','{cat}','{breed}','{color}',{age},{bdd})"
        statements.append(stmt)
    return f"INSERT INTO {table_name} VALUES\n" + ",\n".join(statements) + ";\n\n"

# Generate dictionary inserts
p_witnessed_dict_sql = generate_dict_insert("pw", 100)
p_plays_dict_sql = generate_dict_insert("pp", 100)
p_cares_dict_sql = generate_dict_insert("pc", 100)
p_owns_dict_sql = generate_dict_insert("po", 100)

insert_dict_sql = f"""INSERT INTO _dict(name, dict) VALUES ('performance', 
dictionary('{p_witnessed_dict_sql}{p_plays_dict_sql}{p_cares_dict_sql}{p_owns_dict_sql}
'));\n\n"""


# Generate table inserts
p_witnessed_sql = generate_insert_statements("p_witnessed", "pw", 100)
p_plays_sql = generate_insert_statements("p_plays", "pp", 100)
p_cares_sql = generate_insert_statements("p_cares", "pc", 100)
p_owns_sql = generate_insert_statements("p_owns", "po", 100)

# Combine all
full_sql_script = insert_dict_sql + \
                  p_witnessed_sql + p_plays_sql + p_cares_sql + p_owns_sql

preview = "\n".join(full_sql_script.splitlines())


# NOTE: The code is not sent to PostgreSQL right away,
#       but written to a file for cautious manual execution.
# NOTE: Make sure the tables are created and empty. Make sure the dict is not yet created.
#       These are not handled in this script.
print(preview)

with open("sql/performance_insert.sql", "w", encoding="utf-8") as f:
    f.write(preview)
print("SQL script written to sql/performance_insert.sql")

