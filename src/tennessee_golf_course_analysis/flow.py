from pathlib import Path
import subprocess

from prefect import flow, task, get_run_logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DBT_DIR = PROJECT_ROOT / "tennessee_golf_course_analysis"


def run_command(command: list[str], cwd: Path) -> None:
    logger = get_run_logger()
    logger.info("Running: %s", " ".join(command))

    subprocess.run(command, cwd=cwd, check=True)


@task(name="Extract OpenGolfAPI Data", retries=2, retry_delay_seconds=30)
def extract_data():
    run_command(
        ["uv", "run", "python", "-m", "tennessee_golf_course_analysis.extract"],
        PROJECT_ROOT,
    )


@task(name="Load Bronze Data")
def load_bronze():
    run_command(
        ["uv", "run", "python", "-m", "tennessee_golf_course_analysis.load"],
        PROJECT_ROOT,
    )


@task(name="Build Silver and Gold")
def run_dbt():
    run_command(
        ["uv", "run", "dbt", "run"],
        DBT_DIR,
    )


@task(name="Validate Data Quality")
def test_dbt():
    run_command(
        ["uv", "run", "dbt", "test"],
        DBT_DIR,
    )


@flow(name="Tennessee Golf Course Pipeline", log_prints=True)
def golf_course_pipeline():
    extract_data()
    load_bronze()
    run_dbt()
    test_dbt()


from prefect.schedules import Cron

if __name__ == "__main__":
    golf_course_pipeline.serve(
        name="tennessee-golf-daily",
        schedule=Cron(
            "0 8 * * *",
            timezone="America/Chicago",
        ),
    )
