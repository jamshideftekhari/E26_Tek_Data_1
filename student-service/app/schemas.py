from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    name: str
    email: str


class StudentOut(StudentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PriorityIn(BaseModel):
    course_id: int
    rank: int  # 1 = highest priority


class PrioritySubmit(BaseModel):
    priorities: list[PriorityIn]


class PriorityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    rank: int
