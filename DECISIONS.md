# Engineering Decisions

## 1. Data Source: OpenGolfAPI

**Decision:** Use OpenGolfAPI to retrieve Tennessee golf course information.

**Reasoning:** OpenGolfAPI provides course information, tee boxes, course ratings, slope ratings, and yardage through an API. This allowed me to collect the information needed to compare golf course difficulty without manually entering data.

**Alternative:** Manually collect course information from individual golf course websites.

**Tradeoff:** Using an API makes extraction easier and repeatable, but the analysis depends on the accuracy, completeness, and availability of the source data.

## 2. Raw Data Storage: Dated JSON Snapshots

**Decision:** Save API responses as JSON files organized by extraction date.

**Reasoning:** Keeping the original responses allows me to preserve source data and troubleshoot extraction or loading problems without immediately requesting the data again.

**Alternative:** Load API responses directly into DuckDB without saving the original data.

**Tradeoff:** Raw snapshots require additional storage, but they provide a record of the extracted data and make troubleshooting easier.

## 3. Analytical Database: DuckDB

**Decision:** Use DuckDB as the analytical database for the Bronze, Silver, and Gold layers.

**Reasoning:** DuckDB works well for local analytical processing and integrates with Python and dbt. It allowed me to build the project without managing a separate database server.

**Alternative:** PostgreSQL.

**Tradeoff:** DuckDB is lightweight and easy to use locally, but it is less suited to applications requiring many concurrent database writers.

## 4. Transformations and Orchestration: dbt and Prefect

**Decision:** Use dbt for SQL transformations and data quality tests, and Prefect for pipeline orchestration.

**Reasoning:** dbt separates transformation logic into organized SQL models and provides automated testing. Prefect manages the execution order of extraction, loading, transformations, testing, and publishing.

**Alternative:** Write one Python script to perform every pipeline step.

**Tradeoff:** Using separate tools adds configuration and dependencies, but it makes the pipeline easier to organize, test, monitor, and troubleshoot.

## 5. Dashboard Data Serving: Separate DuckDB Database

**Decision:** Publish the Gold models into a separate DuckDB database for the Streamlit dashboard.

**Reasoning:** Separating the serving database from the analytical warehouse allows the dashboard to query published results without interfering with pipeline transformations. The publishing process replaces the serving database after validation succeeds.

**Alternative:** Have Streamlit query the main analytical DuckDB warehouse directly.

**Tradeoff:** Maintaining a second database adds a publishing step and duplicates the Gold data, but it separates dashboard access from pipeline processing and helps avoid database access conflicts.