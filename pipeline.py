import sys

import pandas as pd
from sqlalchemy import create_engine, text

URL = "https://raw.githubusercontent.com/owid-co2-data/master/owid-co2-data.csv"
DB = "postgresql+psycopg2://postgres:pass@localhost:5432/postgres"

COLS = ["country", "year", "iso_code", "population", "gdp", "co2", "co2_per_capita"]

# Each check contains a name and a query that counts problematic rows.
# All checks should return 0 to pass.
CHECKS = [
    (
        "fact_co2 is not empty",
        "SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END FROM fact_co2"
    ),
    (
        "dim_country contains no non-country OWID entries",
        "SELECT COUNT(*) FROM dim_country WHERE LEFT(iso_code, 4) = 'OWID'"
    ),
    (
        "fact_co2 has no NULL iso_code or year",
        "SELECT COUNT(*) FROM fact_co2 WHERE iso_code IS NULL OR year IS NULL"
    ),
    (
        "fact_co2 has no NULL or negative CO2 values",
        "SELECT COUNT(*) FROM fact_co2 WHERE co2 IS NULL OR co2 < 0"
    ),
    (
        "years are within a reasonable range (1750 to current year)",
        "SELECT COUNT(*) FROM fact_co2 "
        "WHERE year < 1750 OR year > EXTRACT(YEAR FROM CURRENT_DATE)"
    ),
    (
        "there are no duplicate (iso_code, year) combinations",
        "SELECT COUNT(*) FROM (SELECT iso_code, year FROM fact_co2 "
        "GROUP BY iso_code, year HAVING COUNT(*) > 1) d"
    ),
    (
        "all fact_co2 iso_codes exist in dim_country",
        "SELECT COUNT(*) FROM fact_co2 f "
        "LEFT JOIN dim_country d ON f.iso_code = d.iso_code "
        "WHERE d.iso_code IS NULL"
    ),
    (
        "fact_co2 row count does not exceed raw_co2 row count",
        "SELECT CASE WHEN (SELECT COUNT(*) FROM fact_co2) "
        "<= (SELECT COUNT(*) FROM raw_co2) THEN 0 ELSE 1 END"
    ),
]


def extract():
    # Read the CSV file directly from the URL.
    return pd.read_csv(URL)


def load_raw(df):
    engine = create_engine(DB)

    # Load the raw data without applying transformations.
    # "replace" recreates the table every time the pipeline runs.
    df[COLS].to_sql("raw_co2", engine, if_exists="replace", index=False)


def transform():
    engine = create_engine(DB)

    # Read the SQL transformation script.
    with open("transform.sql", encoding="utf-8") as f:
        sql = f.read()

    # begin() automatically rolls back the transaction if an error occurs.
    with engine.begin() as conn:
        for statement in sql.split(";"):
            if statement.strip():
                conn.exec_driver_sql(statement)


def validate():
    engine = create_engine(DB)
    failed = []

    with engine.connect() as conn:
        for name, query in CHECKS:
            bad_rows = conn.execute(text(query)).scalar()

            status = "OK  " if bad_rows == 0 else "FAIL"
            print(f"[{status}] {name} (problematic rows: {bad_rows})")

            if bad_rows != 0:
                failed.append(name)

        n_raw = conn.execute(
            text("SELECT COUNT(*) FROM raw_co2")
        ).scalar()

        n_fact = conn.execute(
            text("SELECT COUNT(*) FROM fact_co2")
        ).scalar()

        print(f"Row count: raw={n_raw}, fact={n_fact}")

    if failed:
        print(f"\nValidation FAILED: {len(failed)} check(s) failed.")
        sys.exit(1)

    print("\nAll validation checks passed!")


if __name__ == "__main__":
    df = extract()

    print(f"Dataset shape: {df.shape}")
    print("\nMissing values:")
    print(df[COLS].isna().sum())

    load_raw(df)
    print("\nRaw data loaded successfully.")

    transform()
    print("Transformation completed successfully.")

    validate()
