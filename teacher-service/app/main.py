import os

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

MANAGEMENT_SERVICE_URL = os.environ.get(
    "MANAGEMENT_SERVICE_URL", "http://management-service:8003"
)

app = FastAPI(title="Teacher Service")


def _get_course_or_404(course_id: int, db: Session) -> models.Course:
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


def _fetch_course_schedule(course_id: int) -> dict:
    try:
        resp = httpx.get(
            f"{MANAGEMENT_SERVICE_URL}/schedule/course/{course_id}", timeout=10
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Management service unavailable") from exc
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="No schedule yet for this course")
    resp.raise_for_status()
    return resp.json()


@app.post("/courses", response_model=schemas.CourseOut)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@app.get("/courses", response_model=list[schemas.CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()


@app.get("/courses/{course_id}/schedule")
def get_course_schedule(course_id: int, db: Session = Depends(get_db)):
    _get_course_or_404(course_id, db)
    return _fetch_course_schedule(course_id)


@app.get("/courses/{course_id}/class-list")
def get_class_list(course_id: int, db: Session = Depends(get_db)):
    course = _get_course_or_404(course_id, db)
    schedule = _fetch_course_schedule(course_id)
    return {
        "course": schemas.CourseOut.model_validate(course).model_dump(),
        "room_id": schedule["room_id"],
        "time_slot": schedule["time_slot"],
        "student_ids": schedule["student_ids"],
    }
