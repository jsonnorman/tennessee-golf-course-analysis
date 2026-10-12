# Tennessee Golf Course Difficulty Analysis

## Project Overview

This project is an end-to-end data engineering pipeline that analyzes golf course difficulty across Tennessee using data from OpenGolfAPI.

The pipeline extracts golf course information, stores raw data in dated JSON snapshots, loads the data into DuckDB, and transforms it using dbt through Bronze, Silver, and Gold data layers.

The Gold layer provides course difficulty metrics and rankings based on course ratings and slope ratings, allowing comparisons across Tennessee golf courses and tee boxes.

Prefect orchestrates the complete pipeline, including data extraction, loading, transformation, data quality testing, and publishing. The pipeline is configured to run daily at 8:00 AM Central Time.

A Streamlit dashboard provides interactive visualizations of the Gold data, allowing users to explore course difficulty rankings and compare course ratings against slope ratings.

## Technologies Used

- **Python:** API extraction, data loading, and publishing
- **OpenGolfAPI:** Golf course data source
- **DuckDB:** Local analytical warehouse and separate serving database
- **dbt:** SQL transformations and data quality tests
- **Prefect:** Pipeline orchestration, retries, and scheduling
- **Streamlit:** Interactive dashboard
- **Altair:** Data visualizations
- **uv:** Python dependency management

## Data Source

The project uses OpenGolfAPI to retrieve golf course information for Tennessee.

The extracted data includes:

- Golf course names and locations
- Tee box information
- Course ratings
- Slope ratings
- Course par and yardage

The pipeline retrieves the Tennessee course list and then requests detailed information for each course.

Raw API responses are saved as dated JSON snapshots under:

`data/raw/YYYY-MM-DD/`

Each snapshot contains:

- `tennessee_courses.json`
- `tennessee_course_details.json`

These files preserve the extracted source data and allow the pipeline to reload previously collected data.

## Pipeline Architecture

The pipeline follows a Bronze, Silver, and Gold architecture.

### 1. Extract

Python retrieves Tennessee golf course data from OpenGolfAPI and saves the raw responses as JSON files.

### 2. Bronze

The loading process imports the raw JSON data into DuckDB.

Bronze tables:

- `bronze.courses`
- `bronze.course_details`

### 3. Silver

dbt transforms the raw data into structured, analysis-ready views.

Silver models:

- `silver_courses`
- `silver_tees`

These models organize course information and tee box measurements into consistent records.

### 4. Gold

dbt builds two analytical models:

- `gold_course_difficulty`: Course and tee box difficulty measurements
- `gold_course_rankings`: Course difficulty rankings by gender

Course ratings are used as the primary ranking metric, with slope rating and yardage used as additional sorting criteria.

### 5. Data Quality

dbt runs 10 automated tests, including:

- Required-field checks
- Unique course identifiers
- Relationships between courses and tee boxes

The pipeline must pass these tests before publishing.

### 6. Publish

After successful validation, Python creates a separate DuckDB serving database containing physical copies of the Gold models.

The serving database is located at:

`data/serving/warehouse.duckdb`

This separates dashboard queries from the main analytical warehouse.

### 7. Dashboard

Streamlit reads the published Gold data and provides:

- Top 10 most difficult courses by course rating
- Male and female tee filtering
- Course rating versus slope rating comparisons
- Interactive charts and detailed course information

## Setup and Running the Project

### Prerequisites

- Python 3.14
- uv
- Git

### Install Dependencies

Clone the repository and install the project dependencies:

```bash
git clone YOUR_REPOSITORY_URL
cd tennessee-golf-course-analysis
uv sync
```

Replace `YOUR_REPOSITORY_URL` with the project's GitHub URL.

### Run the Pipeline

Start the Prefect server in one terminal:

```bash
uv run prefect server start
```

In a second terminal, configure the Prefect API connection:

```bash
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

Start the deployment:

```bash
uv run python -m tennessee_golf_course_analysis.flow
```

The deployment is scheduled to run daily at 8:00 AM Central Time while the local Prefect services are running.

To trigger a pipeline run manually, open another terminal and execute:

```bash
uv run prefect deployment run 'Tennessee Golf Course Pipeline/tennessee-golf-daily'
```

The pipeline automatically extracts, loads, transforms, validates, and publishes the data.

### Launch the Dashboard

After the first successful pipeline run, launch Streamlit:

```bash
uv run streamlit run app.py
```

The dashboard reads the published Gold tables from `data/serving/warehouse.duckdb`.

## Orchestration and Scheduling

Prefect manages the pipeline through five sequential tasks:

1. Extract OpenGolfAPI Data
2. Load Bronze Data
3. Build Silver and Gold
4. Validate Data Quality
5. Publish Gold Data

The extraction task is configured with two retries and a 30-second delay between retries.

The pipeline is scheduled daily at 8:00 AM Central Time using the `America/Chicago` timezone.

A successful deployment-triggered run was verified on October 12, 2026, with all five tasks completing.

## Current Results

During the October 12, 2026 pipeline execution:

- 212 Tennessee golf course records were retrieved.
- 207 courses had tee box information.
- 651 valid tee configurations were included in the Gold difficulty model.
- 237 course-and-gender ranking records were published.
- All 10 dbt data quality tests passed.

These counts reflect the source data at the time of execution and may change during future refreshes.

## Limitations

Course difficulty is evaluated using published course ratings, with slope ratings and yardage used as secondary ranking criteria.

Course rating estimates the expected score for a scratch golfer, while slope rating describes relative difficulty for a bogey golfer compared with a scratch golfer. These measurements describe different aspects of difficulty and should not be interpreted as interchangeable.

The analysis depends on the availability and completeness of OpenGolfAPI records. Some courses or tee boxes may have missing ratings or slope values and may therefore be excluded from the Gold analysis.

The rankings also apply a minimum course rating of 60 to exclude likely nine-hole ratings from the course-level comparison. This is a provisional filtering rule rather than a definitive method for identifying nine-hole courses.

The daily Prefect schedule requires the local Prefect server and deployment process to remain running.

### Data Source Attribution and Updates

**Source:** [OpenGolfAPI](https://opengolfapi.org/)

**API endpoints:**
- Tennessee courses: `https://api.opengolfapi.org/api/v1/courses/state/TN`
- Course details: `https://api.opengolfapi.org/api/v1/courses/{course_id}`

**License:** Open Data Commons Open Database License (ODbL) 1.0.

**Required attribution:** © OpenStreetMap contributors (ODbL 1.0) via OpenGolfAPI.

**Terms of service:** https://courses.opengolfapi.org/legal/terms

OpenGolfAPI is a community-maintained dataset. Its records are updated over time, but a guaranteed source refresh frequency has not been established.

This project's Prefect pipeline is configured to retrieve fresh API data daily at 8:00 AM Central Time. The extraction schedule does not guarantee that the upstream data changes each day.