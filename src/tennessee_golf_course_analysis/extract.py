import httpx

COURSES_URL = "https://api.opengolfapi.org/api/v1/courses/state/TN"


def fetch_courses():
    response = httpx.get(COURSES_URL, params={"limit": 500})
    response.raise_for_status()

    data = response.json()
    return data["courses"]


def fetch_course_details(course_id):
    url = f"https://api.opengolfapi.org/api/v1/courses/{course_id}"

    response = httpx.get(url)
    response.raise_for_status()

    return response.json()


def main():
    courses = fetch_courses()

    print(f"Retrieved {len(courses)} Tennessee courses")

    for course in courses[:5]:
        details = fetch_course_details(course["id"])
        tees = details.get("tees", [])

        print(f"\n{details['course_name']}")
        print(f"Tees: {len(tees)}")

        for tee in tees:
            print(
                tee.get("tee_name"),
                tee.get("gender"),
                tee.get("course_rating"),
                tee.get("slope"),
                tee.get("yardage"),
            )


if __name__ == "__main__":
    main()
