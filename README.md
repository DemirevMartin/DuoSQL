# Probabilistic SQL 

## Module 12 - Research Project

This project is a part of the topic "A probabilistic approach towards handling data quality problems and imperfect data integration tasks" of the Data Science track.

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