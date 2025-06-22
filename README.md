# DuoSQL: A High-Level Query Language for Probabilistic Databases

## University of Twente - TCS Bachelor's Research Project

This project is a part of the topic "A probabilistic approach towards handling data quality problems and imperfect data integration tasks" of the Data Science track.

---

## Project Structure Overview

This repository implements **DuoSQL**, a high-level query language and translation system for **DuBio**, along with an experiment pipeline for evaluation.

### Translation Layer
- `main.py`: Core implementation of the DuoSQL-to-DuBio SQL compiler algorithm.
- `test_duosql_postgresql.py`: Provides a method to test DuoSQL queries by translating and sending them for evaluation to PostgreSQL. The retrieved result is displayed.

### Experiments & Evaluation
- `high_level_tests.py`: 
    - Contains the high-level DuoSQL queries used during the experiments. 
    - Contains translation testing - from high-level code to automatic.
- `experiment_runner.py`: Generates Excel files for each experiment's test type and selected queries. There are 4 criteria: code lines, characters, level of complexity, and probabilistic constructs.
- `experiment_visualizer.ipynb`: Generates visualizations - bar charts and summary tables - based on the Excel files.
- `experiment_results/`: Contains output Excel files from the `experiment_runner` and subfolders with generated diagrams for each experiment from the `experiment_visualizer`.

### SQL Logic & Schema
- `sql/`:
  - Contains the DuBio SQL code for BDD-based aggregation functions.
  - Includes table definitions and sample data for the experiments.

### Manual and Automatic Translations of High-level Queries
- `translations/`: Holds manually and automatically generated DuBio SQL queries for the experiments.

### Performance evaluation
- `performance_evaluation/`:
  - `automatic_queries.py`: Contains the Automatic queries with a modifiable `LIMIT` clause used in the benchmark.
  - `manual_queries.py`: Contains the Manual queries with a modifiable `LIMIT` clause used in the benchmark.
  - `data_generator.py`: Generates data and SQL code to insert it, and saves it to `sql/performance_insert.sql`. Does **not** transmit to PostgreSQL - everything must be executed manually with caution.
  - `performance_benchmark.ipynb`: Contains the benchmark code that sends queries to PostgreSQL and measures and records their execution times.

---

## Prerequisites

- **Python 3.10+**
- A terminal or command prompt

---

## 1. Install Dependencies

Before running any part of the application, install required packages.

```bash
python -m venv .venv             # Create virtual environment
# Activate the venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt   # Install Python dependencies
```


## 2. Environment Variables

1. Copy `.env.example` to `.env` in the main project directory.
2. Fill the database credentials in the placeholders:

   ```ini
   USER=<POSTGRES_USER>
   PASSWORD=<POSTGRES_PASSWORD>
   HOST=<POSTGRES_HOST>
   DATABASE=<POSTGRES_DB>
   ```