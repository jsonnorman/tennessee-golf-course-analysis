WITH ranked_courses AS (
    SELECT
        c.id,
        c.course_name,
        c.city,
        c.state,
        c.country_iso,
        c.lat,
        c.lng,
        c.type AS course_type,
        c.par,
        c.holes,
        c.completeness,

        ROW_NUMBER() OVER (
            PARTITION BY LOWER(TRIM(c.course_name))
            ORDER BY
                COALESCE(
                    LEN(
                        LIST_FILTER(
                            d.holes_data,
                            h -> h.yardages IS NOT NULL
                        )
                    ),
                    0
                ) DESC,
                c.completeness DESC NULLS LAST,
                c.id
        ) AS row_num

    FROM {{ source('bronze', 'courses') }} c
    LEFT JOIN {{ source('bronze', 'course_details') }} d
        ON c.id = d.id
)

SELECT
    id,
    course_name,
    city,
    state,
    country_iso,
    lat,
    lng,
    course_type,
    par,
    holes,
    completeness
FROM ranked_courses
WHERE row_num = 1