import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

BASE_URL = "https://osu.instructure.com/api/v1"
TOKEN = os.getenv("CANVAS_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}


def parse_canvas_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_current_semester(course, target_term="Spring 2026"):
    term = course.get("term") or {}
    term_name = term.get("name", "").strip()
    return term_name.lower() == target_term.lower()


def paginate(url):
    results = []

    while url:
        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            return results

        results.extend(r.json())

        if "next" in r.links:
            url = r.links["next"]["url"]
        else:
            url = None

    return results


def dump_canvas():

    dump = {
        "courses": [],
        "calendar_events": []
    }

    now = datetime.now(timezone.utc)

    courses = paginate(
        f"{BASE_URL}/courses?enrollment_state=active&include[]=term&per_page=50"
    )

    current_semester_courses = [
        course for course in courses
        if is_current_semester(course)
    ]

    for course in current_semester_courses:

        cid = course["id"]

        syllabus = requests.get(
            f"{BASE_URL}/courses/{cid}?include[]=syllabus_body",
            headers=headers
        ).json()

        raw_assignments = paginate(
            f"{BASE_URL}/courses/{cid}/assignments?per_page=50"
        )

        upcoming_assignments = []

        for assignment in raw_assignments:

            if not assignment.get("published"):
                continue

            due_at = assignment.get("due_at")
            if not due_at:
                continue

            due_date = parse_canvas_datetime(due_at)
            if not due_date:
                continue

            if due_date < now:
                continue

            upcoming_assignments.append({
                "id": assignment.get("id"),
                "name": assignment.get("name"),
                "due_at": due_at,
                "due_datetime": due_date,  # store parsed datetime
                "points_possible": assignment.get("points_possible"),
                "course_id": cid
            })

        # Sort safely using stored datetime
        upcoming_assignments.sort(key=lambda x: x["due_datetime"])

        # Remove helper field before returning
        for a in upcoming_assignments:
            del a["due_datetime"]

        dump["courses"].append({
            "metadata": {
                "id": course.get("id"),
                "name": course.get("name"),
                "course_code": course.get("course_code")
            },
            "syllabus": syllabus.get("syllabus_body"),
            "assignments": upcoming_assignments
        })

    dump["calendar_events"] = paginate(
        f"{BASE_URL}/calendar_events?per_page=50"
    )

    return dump