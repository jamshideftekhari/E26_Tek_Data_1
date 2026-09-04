from collections import defaultdict

from models import allocation_model, course_model, priority_model, room_model, schedule_model


def run_allocation():
    """Priority-first-fit: each student gets their highest-ranked course that
    still has a free seat, bounded by the capacity of the room paired with it.
    """
    courses = course_model.get_all_courses()
    priorities = priority_model.get_all_priorities()
    rooms = room_model.get_all_rooms()

    # Pair courses with rooms in order; courses beyond the number of
    # available rooms cannot be scheduled in this MVP.
    course_room = dict(zip((c["id"] for c in courses), rooms))
    course_capacity = {c["id"]: c["capacity"] for c in courses}
    seats_left = {
        course_id: min(course_capacity[course_id], room["capacity"])
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

    allocation_model.clear_allocations()
    schedule_model.clear_schedule()

    for course_id, room in course_room.items():
        schedule_id = schedule_model.create_schedule_entry(
            course_id=course_id, room_id=room["id"], time_slot=room["time_slot"]
        )
        for student_id in assignments.get(course_id, []):
            allocation_model.create_allocation(
                schedule_id=schedule_id, student_id=student_id
            )

    return {
        "courses_scheduled": len(course_room),
        "students_allocated": sum(len(v) for v in assignments.values()),
        "unallocated_students": unallocated,
    }


def get_full_schedule():
    rows = schedule_model.get_all_schedule()
    result = []
    for row in rows:
        allocations = allocation_model.get_allocations_for_schedule(row["id"])
        result.append(
            {
                "course_id": row["course_id"],
                "room_id": row["room_id"],
                "time_slot": row["time_slot"],
                "student_ids": [a["student_id"] for a in allocations],
            }
        )
    return result


def priorities_summary():
    courses = course_model.get_all_courses()
    priorities = priority_model.get_all_priorities()

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
