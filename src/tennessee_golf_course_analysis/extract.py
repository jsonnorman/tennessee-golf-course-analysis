import httpx
import time

COURSES_URL = "https://api.opengolfapi.org/api/v1/courses/state/TN"


def fetch_courses(client):
    response = client.get(COURSES_URL, params={"limit": 500})
    response.raise_for_status()

    data = response.json()
    return data["courses"]


def fetch_course_details(client, course_id):
    url = f"https://api.opengolfapi.org/api/v1/courses/{course_id}"

    for attempt in range(3):
        response = client.get(url)

        if response.status_code == 429:
            wait_seconds = 10 * (attempt + 1)
            print(f"Rate limited. Waiting {wait_seconds} seconds...")
            time.sleep(wait_seconds)
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError(f"Failed to fetch course {course_id} after 3 attempts")


def main():
    transport = httpx.HTTPTransport(retries=3)

    with httpx.Client(transport=transport, timeout=30.0) as client:
        courses = fetch_courses(client)

        print(f"Retrieved {len(courses)} Tennessee courses")

        total_courses = len(courses)
        courses_with_tees = 0
        total_tees = 0
        tees_with_rating = 0
        tees_with_slope = 0
        tees_with_both = 0

        for index, course in enumerate(courses, start=1):
            details = fetch_course_details(client, course["id"])
            time.sleep(0.25)
            tees = details.get("tees", [])

            print(f"[{index}/{total_courses}] {details['course_name']}")

            if tees:
                courses_with_tees += 1

            total_tees += len(tees)

            for tee in tees:
                rating = tee.get("course_rating")
                slope = tee.get("slope")

                if rating is not None:
                    tees_with_rating += 1

                if slope is not None:
                    tees_with_slope += 1

                if rating is not None and slope is not None:
                    tees_with_both += 1

        print("\n--- Tennessee Data Summary ---")
        print(f"Courses: {total_courses}")
        print(f"Courses with tees: {courses_with_tees}")
        print(f"Total tee records: {total_tees}")
        print(f"Tees with course rating: {tees_with_rating}")
        print(f"Tees with slope: {tees_with_slope}")
        print(f"Tees with both rating and slope: {tees_with_both}")


if __name__ == "__main__":
    main()
