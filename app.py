from pathlib import Path

import altair as alt
import duckdb
import streamlit as st

# --------------------------------------------------
# Configuration
# --------------------------------------------------

SERVING_DB = Path(__file__).resolve().parent / "data" / "serving" / "warehouse.duckdb"

st.set_page_config(
    page_title="Tennessee Golf Course Difficulty",
    page_icon="⛳",
    layout="wide",
)


# --------------------------------------------------
# Load Gold Data
# --------------------------------------------------


@st.cache_data
def load_rankings():
    with duckdb.connect(str(SERVING_DB), read_only=True) as con:
        return con.execute("""
            SELECT
                course_id,
                course_name,
                city,
                tee_name,
                gender,
                course_rating,
                slope,
                par,
                yardage,
                difficulty_rank
            FROM main.gold_course_rankings
            ORDER BY difficulty_rank, course_name
        """).df()


@st.cache_data
def load_difficulty():
    with duckdb.connect(str(SERVING_DB), read_only=True) as con:
        return con.execute("""
            SELECT
                course_id,
                course_name,
                city,
                tee_name,
                gender,
                course_rating,
                slope,
                par,
                yardage
            FROM main.gold_course_difficulty
            ORDER BY course_name, tee_name
        """).df()


rankings = load_rankings()
difficulty = load_difficulty()


# --------------------------------------------------
# Dashboard Header
# --------------------------------------------------

st.title("⛳ Tennessee Golf Course Difficulty Analysis")

st.write(
    "Explore and compare Tennessee golf courses using "
    "official course ratings, slope ratings, and tee information."
)

st.caption(
    "Data source: OpenGolfAPI | "
    "Warehouse: DuckDB | "
    "Transformations: dbt | "
    "Orchestration: Prefect"
)

st.divider()


# --------------------------------------------------
# Filters
# --------------------------------------------------

genders = sorted(difficulty["gender"].dropna().unique().tolist())

selected_gender = st.selectbox(
    "Select Gender Category",
    genders,
)

filtered_rankings = rankings[rankings["gender"] == selected_gender].copy()

filtered_difficulty = difficulty[difficulty["gender"] == selected_gender].copy()

top_10 = (
    filtered_rankings.sort_values(["difficulty_rank", "course_name"]).head(10).copy()
)


# --------------------------------------------------
# Summary Metrics
# --------------------------------------------------

total_courses = difficulty["course_id"].nunique()
total_tees = len(difficulty)
filtered_courses = filtered_difficulty["course_id"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("Tennessee Courses Analyzed", f"{total_courses:,}")
col2.metric("Valid Tee Configurations", f"{total_tees:,}")
col3.metric(
    f"{selected_gender} Courses",
    f"{filtered_courses:,}",
)

st.divider()


# --------------------------------------------------
# View 1: Hardest Golf Courses
# --------------------------------------------------

st.header("1. Hardest Tennessee Golf Courses")

st.caption(
    "Courses are ranked by their highest qualifying course "
    "rating within the selected gender category."
)

st.subheader("Top 10 Courses by Course Rating")

# Sort by rating so the highest value appears first.
# Altair handles the display order explicitly.
bar_chart = (
    alt.Chart(top_10)
    .mark_bar(color="#268566", cornerRadiusEnd=4)
    .encode(
        x=alt.X(
            "course_rating:Q",
            title="Course Rating",
            scale=alt.Scale(zero=False),
        ),
        y=alt.Y(
            "course_name:N",
            title=None,
            sort=alt.SortField(
                field="difficulty_rank",
                order="ascending",
            ),
        ),
        tooltip=[
            alt.Tooltip("difficulty_rank:Q", title="Rank"),
            alt.Tooltip("course_name:N", title="Golf Course"),
            alt.Tooltip("city:N", title="City"),
            alt.Tooltip("tee_name:N", title="Tee Box"),
            alt.Tooltip("course_rating:Q", title="Course Rating"),
            alt.Tooltip("slope:Q", title="Slope Rating"),
            alt.Tooltip("par:Q", title="Par"),
            alt.Tooltip("yardage:Q", title="Yardage"),
        ],
    )
    .properties(height=430)
)

st.altair_chart(bar_chart, use_container_width=True)

st.subheader("Top 10 Rankings")

st.dataframe(
    top_10[
        [
            "difficulty_rank",
            "course_name",
            "city",
            "tee_name",
            "course_rating",
            "slope",
            "par",
            "yardage",
        ]
    ].rename(
        columns={
            "difficulty_rank": "Rank",
            "course_name": "Golf Course",
            "city": "City",
            "tee_name": "Tee Box",
            "course_rating": "Course Rating",
            "slope": "Slope Rating",
            "par": "Par",
            "yardage": "Yardage",
        }
    ),
    hide_index=True,
    use_container_width=True,
)

st.divider()


# --------------------------------------------------
# View 2: Course Rating vs. Slope Rating
# --------------------------------------------------

st.header("2. Course Rating vs. Slope Rating")

st.caption(
    "Course rating estimates difficulty for a scratch golfer, "
    "while slope rating describes relative difficulty for a "
    "bogey golfer compared with a scratch golfer."
)

st.subheader("How Course Rating and Slope Compare")

scatter_chart = (
    alt.Chart(filtered_difficulty)
    .mark_circle(
        size=90,
        color="#268566",
        opacity=0.7,
    )
    .encode(
        x=alt.X(
            "course_rating:Q",
            title="Course Rating",
            scale=alt.Scale(zero=False),
        ),
        y=alt.Y(
            "slope:Q",
            title="Slope Rating",
            scale=alt.Scale(zero=False),
        ),
        tooltip=[
            alt.Tooltip("course_name:N", title="Golf Course"),
            alt.Tooltip("city:N", title="City"),
            alt.Tooltip("tee_name:N", title="Tee Box"),
            alt.Tooltip("gender:N", title="Gender"),
            alt.Tooltip(
                "course_rating:Q",
                title="Course Rating",
                format=".1f",
            ),
            alt.Tooltip("slope:Q", title="Slope Rating"),
            alt.Tooltip("par:Q", title="Par"),
            alt.Tooltip("yardage:Q", title="Yardage"),
        ],
    )
    .properties(height=500)
    .interactive()
)

st.altair_chart(scatter_chart, use_container_width=True)

st.caption(
    "Each point represents a tee configuration. "
    "Hover over a point to identify its golf course and tee box. "
    "Higher values generally indicate greater difficulty, "
    "although course rating and slope measure different things."
)


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Tennessee Golf Course Difficulty Analysis | "
    "Nashville Software School — Data Engineering Final Project"
)
