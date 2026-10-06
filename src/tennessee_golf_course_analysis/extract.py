import httpx
import time
import json
from pathlib import Path
from datetime import date

COURSES_URL = "https://api.opengolfapi.org/api/v1/courses/state/TN"
RAW_DIR = Path("data/raw")


def fetch_courses(client):
    response = client.get(COURSES_URL, params={"limit": 500})
    response.raise_for_status()

    return response.json()


def save_raw_data(data, filename):
    snapshot_date = date.today().isoformat()
    snapshot_dir = RAW_DIR / snapshot_date

    snapshot_dir.mkdir(parents=True, exist_ok=True)

    file_path = snapshot_dir / filename

    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

    print(f"Saved raw data to {file_path}")


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
        courses_response = fetch_courses(client)
        courses = courses_response["courses"]

        print(f"Retrieved {len(courses)} Tennessee courses")

        save_raw_data(courses_response, "tennessee_courses.json")

        total_courses = len(courses)
        courses_with_tees = 0
        total_tees = 0
        tees_with_rating = 0
        tees_with_slope = 0
        tees_with_both = 0

        all_course_details = []

        for index, course in enumerate(courses, start=1):
            details = fetch_course_details(client, course["id"])
            all_course_details.append(details)

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

        save_raw_data(all_course_details, "tennessee_course_details.json")

        print("\n--- Tennessee Data Summary ---")
        print(f"Courses: {total_courses}")
        print(f"Courses with tees: {courses_with_tees}")
        print(f"Total tee records: {total_tees}")
        print(f"Tees with course rating: {tees_with_rating}")
        print(f"Tees with slope: {tees_with_slope}")
        print(f"Tees with both rating and slope: {tees_with_both}")


if __name__ == "__main__":
    main()
