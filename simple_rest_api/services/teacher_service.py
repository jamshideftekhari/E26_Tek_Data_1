from models import allocation_model, course_model, schedule_model
from services.errors import NotFoundError


def create_course(data):
    return course_model.create_course(
        teacher_name=data["teacher_name"],
        code=data["code"],
        title=data["title"],
        description=data.get("description"),
        capacity=data["capacity"],
    )


def list_courses():
    return course_model.get_all_courses()


def get_course_schedule(course_id):
    if not course_model.get_course(course_id):
        raise NotFoundError("Course not found")
    schedule = schedule_model.get_schedule_for_course(course_id)
    if not schedule:
        raise NotFoundError("No schedule yet for this course")
    allocations = allocation_model.get_allocations_for_schedule(schedule["id"])
    schedule["student_ids"] = [a["student_id"] for a in allocations]
    return schedule


def get_class_list(course_id):
    course = course_model.get_course(course_id)
    if not course:
        raise NotFoundError("Course not found")
    schedule = get_course_schedule(course_id)
    return {
        "course": course,
        "room_id": schedule["room_id"],
        "time_slot": schedule["time_slot"],
        "student_ids": schedule["student_ids"],
    }
