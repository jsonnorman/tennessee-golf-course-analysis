SELECT
    c.id AS course_id,
    c.course_name,
    c.city,
    c.state,
    t.tee_key,
    t.tee_name,
    t.tee_color,
    t.gender,
    t.course_rating,
    t.slope,
    t.par,
    t.yardage
FROM {{ ref('silver_courses') }} AS c
INNER JOIN {{ ref('silver_tees') }} AS t
    ON c.id = t.course_id
WHERE
    t.course_rating > 0
    AND t.slope BETWEEN 55 AND 155