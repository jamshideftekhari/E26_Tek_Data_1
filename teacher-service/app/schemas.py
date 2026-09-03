from pydantic import BaseModel, ConfigDict


class CourseCreate(BaseModel):
    teacher_name: str
    code: str
    title: str
    description: str | None = None
    capacity: int


class CourseOut(CourseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
