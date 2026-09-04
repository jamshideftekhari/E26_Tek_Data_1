from models import allocation_model, schedule_model, student_model, priority_model
from services.errors import NotFoundError


def create_student(data):
    return student_model.create_student(name=data["name"], email=data["email"])


def submit_priorities(student_id, priorities):
    if not student_model.get_student(student_id):
        raise NotFoundError("Student not found")
    return priority_model.replace_priorities(student_id, priorities)


def get_student_schedule(student_id):
    if not student_model.get_student(student_id):
        raise NotFoundError("Student not found")
    allocation = allocation_model.get_allocation_for_student(student_id)
    if not allocation:
        raise NotFoundError("No schedule yet for this student")
    schedule = schedule_model.get_schedule_by_id(allocation["schedule_id"])
    return {
        "course_id": schedule["course_id"],
        "room_id": schedule["room_id"],
        "time_slot": schedule["time_slot"],
    }
