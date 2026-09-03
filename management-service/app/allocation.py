import os
from collections import defaultdict

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models

TEACHER_SERVICE_URL = os.environ.get("TEACHER_SERVICE_URL", "http://teacher-service:8001")
STUDENT_SERVICE_URL = os.environ.get("STUDENT_SERVICE_URL", "http://student-service:8002")


def _fetch_courses() -> list[dict]:
    try:
        resp = httpx.get(f"{TEACHER_SERVICE_URL}/courses", timeout=10)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Teacher service unavailable") from exc
    resp.raise_for_status()
    return resp.json()


def _fetch_priorities() -> list[dict]:
    try:
        resp = httpx.get(f"{STUDENT_SERVICE_URL}/priorities", timeout=10)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Student service unavailable") from exc
    resp.raise_for_status()
    return resp.json()


def run_allocation(db: Session) -> dict:
    """Priority-first-fit: each student gets their highest-ranked course that
    still has a free seat, bounded by the capacity of the room paired with it.
    """
    courses = _fetch_courses()
    priorities = _fetch_priorities()
    rooms = db.query(models.Room).order_by(models.Room.id).all()

    # Pair courses with rooms in order; courses beyond the number of
    # available rooms cannot be scheduled in this MVP.
    course_room = dict(zip((c["id"] for c in courses), rooms))
    course_capacity = {c["id"]: c["capacity"] for c in courses}
    seats_left = {
        course_id: min(course_capacity[course_id], room.capacity)
        for course_id, room in course_room.items()
    }

    priorities_by_student = defaultdict(list)
    for p in priorities:
        priorities_by_student[p["student_id"]].append(p)
    for plist in priorities_by_student.values():
        plist.sort(key=lambda p: p["rank"])

    assignments = defaultdict(list)  # course_id -> [student_id]
    unallocated = []
    for student_id in sorted(priorities_by_student):
        for p in priorities_by_student[student_id]:
            course_id = p["course_id"]
            if seats_left.get(course_id, 0) > 0:
                assignments[course_id].append(student_id)
                seats_left[course_id] -= 1
                break
        else:
            unallocated.append(student_id)

    db.query(models.Allocation).delete()
    db.query(models.Schedule).delete()
    db.flush()

    for course_id, room in course_room.items():
        schedule_row = models.Schedule(
            course_id=course_id, room_id=room.id, time_slot=room.time_slot
        )
        db.add(schedule_row)
        db.flush()  # populate schedule_row.id for the allocations below
        for student_id in assignments.get(course_id, []):
            db.add(models.Allocation(schedule_id=schedule_row.id, student_id=student_id))

    db.commit()

    return {
        "courses_scheduled": len(course_room),
        "students_allocated": sum(len(v) for v in assignments.values()),
        "unallocated_students": unallocated,
    }


def priorities_summary() -> list[dict]:
    courses = _fetch_courses()
    priorities = _fetch_priorities()

    demand = defaultdict(int)
    for p in priorities:
        demand[p["course_id"]] += 1

    return [
        {
            "course_id": c["id"],
            "code": c["code"],
            "title": c["title"],
            "capacity": c["capacity"],
            "demand": demand.get(c["id"], 0),
        }
        for c in courses
    ]
