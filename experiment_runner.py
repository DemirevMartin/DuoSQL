from translations.automatic_translations import *
from translations.manual_translations import *
from test import *
import re

# LOC (Lines of Code) Counter
# NOTE: If a JOIN clause is present and ON is on a new line, it is NOT counted as 2nd line. It is ALWAYS counted as 1 line.
# This functionality is not implemented and has to be manually checked.
def count_code_lines(query: str):
    # This function counts the number of (non-empty) lines of code in a given query.
    query = query.strip()
    return sum(1 for line in query.splitlines() if line.strip())

# Character Counter
def count_characters(query: str):
    query = query.strip()
    # Do not count larger spaces and semicolons
    query = re.sub(r';|\s+', ' ', query)
    return len(query)

# Probabilistic Constructs Counter (only the relevant ones to this project are included)
def count_probabilistic_constructs(query: str):
    query = query.lower()
    constructs = [r'\bprob\b', r'agg_or', r'prob_Bdd', r'\&', r'_sentence', r'_dict']
    return sum(len(re.findall(construct, query)) for construct in constructs)


if __name__ == "__main__":
    query = test_mixed_data_3
    loc = count_code_lines(query)
    char_count = count_characters(query)
    probabilistic_count = count_probabilistic_constructs(query)

    print(f"Lines of Code: {loc}")
    print(f"Character Count: {char_count}")
    print(f"Probabilistic Constructs Count: {probabilistic_count}")
