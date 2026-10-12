SELECT
    d.id AS course_id,
    d.course_name,
    tee.tee_key,
    tee.tee_name,
    tee.tee_color,
    tee.gender,
    tee.course_rating,
    tee.slope,
    tee.par,
    tee.yardage
FROM {{ source('bronze', 'course_details') }} AS d
INNER JOIN {{ ref('silver_courses') }} AS c
    ON d.id = c.id
CROSS JOIN UNNEST(d.tees) AS t(tee)