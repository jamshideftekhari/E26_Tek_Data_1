from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    name: str
    capacity: int
    time_slot: str


class RoomOut(RoomCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CourseScheduleOut(BaseModel):
    course_id: int
    room_id: int
    time_slot: str
    student_ids: list[int]


class StudentScheduleOut(BaseModel):
    course_id: int
    room_id: int
    time_slot: str


class AllocationSummary(BaseModel):
    courses_scheduled: int
    students_allocated: int
    unallocated_students: list[int]


class CoursePriorityDemand(BaseModel):
    course_id: int
    code: str
    title: str
    capacity: int
    demand: int
