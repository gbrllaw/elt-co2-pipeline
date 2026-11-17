# ELT Pipeline – CO₂ Emissions Data

A simple ELT pipeline project that extracts CO₂ emissions data from Our World in Data, loads it into PostgreSQL, and transforms it using SQL.

## Tech Stack
- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Docker
- SQL

## Pipeline Workflow
1. **Extract:** Retrieve CO₂ emissions data from Our World in Data.
2. **Load:** Store the raw dataset in PostgreSQL (`raw_co2`).
3. **Transform:** Use SQL to create `fact_co2` and `dim_country` tables.
4. **Validate:** Run 8 SQL data quality checks.

## Validation Results
- Raw records: 56,269
- Fact records: 24,109
- Data quality checks: 8/8 passed

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python pipeline.py
```

## Data Source
[Our World in Data – CO₂ and Greenhouse Gas Emissions](https://ourworldindata.org/co2-and-greenhouse-gas-emissions)
