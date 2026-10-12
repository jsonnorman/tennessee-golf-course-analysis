WITH ranked_tees AS (
    SELECT
        course_id,
        course_name,
        city,
        state,
        tee_name,
        tee_color,
        gender,
        course_rating,
        slope,
        par,
        yardage,
        ROW_NUMBER() OVER (
            PARTITION BY course_id, gender
            ORDER BY course_rating DESC, slope DESC, yardage DESC
        ) AS course_tee_rank
    FROM {{ ref('gold_course_difficulty') }}
    WHERE
        course_rating >= 60
        AND gender IN ('Male', 'Female')
)

SELECT
    course_id,
    course_name,
    city,
    state,
    tee_name,
    tee_color,
    gender,
    course_rating,
    slope,
    par,
    yardage,
    ROW_NUMBER() OVER (
        PARTITION BY gender
        ORDER BY course_rating DESC, slope DESC, yardage DESC, course_name
    ) AS difficulty_rank
FROM ranked_tees
WHERE course_tee_rank = 1