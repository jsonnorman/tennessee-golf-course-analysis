from pathlib import Path

import duckdb

DB_PATH = Path("data/warehouse.duckdb")
RAW_DIR = Path("data/raw")


def get_latest_snapshot():
    snapshot_dirs = sorted(path for path in RAW_DIR.iterdir() if path.is_dir())

    if not snapshot_dirs:
        raise FileNotFoundError("No raw snapshots found")

    return snapshot_dirs[-1]


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    latest_snapshot = get_latest_snapshot()
    print(f"Using raw snapshot: {latest_snapshot}")

    with duckdb.connect(str(DB_PATH)) as connection:
        print(f"Connected to DuckDB at {DB_PATH}")

        courses_file = latest_snapshot / "tennessee_courses.json"
        details_file = latest_snapshot / "tennessee_course_details.json"

        connection.execute("CREATE SCHEMA IF NOT EXISTS bronze")

        # Load course listing
        connection.execute(
            """
            CREATE OR REPLACE TABLE bronze.courses AS
            SELECT course.*
            FROM read_json_auto(?),
            UNNEST(courses) AS t(course)
            """,
            [str(courses_file)],
        )

        course_count = connection.execute(
            "SELECT COUNT(*) FROM bronze.courses"
        ).fetchone()[0]

        print(f"Loaded {course_count} rows into bronze.courses")

        # Load detailed course data
        connection.execute(
            """
            CREATE OR REPLACE TABLE bronze.course_details AS
            SELECT *
            FROM read_json_auto(?)
            """,
            [str(details_file)],
        )

        detail_count = connection.execute(
            "SELECT COUNT(*) FROM bronze.course_details"
        ).fetchone()[0]

        print(f"Loaded {detail_count} rows into bronze.course_details")


if __name__ == "__main__":
    main()
