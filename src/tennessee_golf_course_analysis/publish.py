from pathlib import Path
import os

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]

WAREHOUSE_DB = PROJECT_ROOT / "data" / "warehouse.duckdb"

SERVING_DIR = PROJECT_ROOT / "data" / "serving"
SERVING_DB = SERVING_DIR / "warehouse.duckdb"
TEMP_DB = SERVING_DIR / "serving_next.duckdb"


def publish_gold():
    # Ensure the serving directory exists.
    SERVING_DIR.mkdir(parents=True, exist_ok=True)

    # Remove any temporary database from an interrupted run.
    TEMP_DB.unlink(missing_ok=True)

    # Escape single quotes in the warehouse path for DuckDB SQL.
    warehouse_path = str(WAREHOUSE_DB).replace("'", "''")

    # Create a fresh serving database.
    with duckdb.connect(str(TEMP_DB)) as destination:

        # Attach the warehouse using the name expected by dbt views.
        destination.execute(f"ATTACH '{warehouse_path}' AS warehouse (READ_ONLY)")

        # Copy Gold views into physical serving tables.
        for table in (
            "gold_course_rankings",
            "gold_course_difficulty",
        ):
            destination.execute(
                f"CREATE TABLE main.{table} AS " f"SELECT * FROM warehouse.main.{table}"
            )

            row_count = destination.execute(
                f"SELECT COUNT(*) FROM main.{table}"
            ).fetchone()[0]

            print(f"Published {table}: {row_count} rows")

        # Release the source warehouse.
        destination.execute("DETACH warehouse")

    # Replace the previous serving database only after
    # the new database has been created successfully.
    os.replace(TEMP_DB, SERVING_DB)

    print(f"Serving database updated: {SERVING_DB}")


if __name__ == "__main__":
    publish_gold()
