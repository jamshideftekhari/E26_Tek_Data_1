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

app = FastAPI(title="Student Service")


def _get_student_or_404(student_id: int, db: Session) -> models.Student:
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post("/students", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/students", response_model=list[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@app.post("/students/{student_id}/priorities", response_model=list[schemas.PriorityOut])
def submit_priorities(
    student_id: int, payload: schemas.PrioritySubmit, db: Session = Depends(get_db)
):
    _get_student_or_404(student_id, db)

    db.query(models.Priority).filter(models.Priority.student_id == student_id).delete()
    db.add_all(
        models.Priority(student_id=student_id, course_id=p.course_id, rank=p.rank)
        for p in payload.priorities
    )
    db.commit()
    return (
        db.query(models.Priority)
        .filter(models.Priority.student_id == student_id)
        .order_by(models.Priority.rank)
        .all()
    )


@app.get("/priorities", response_model=list[schemas.PriorityOut])
def list_priorities(db: Session = Depends(get_db)):
    return db.query(models.Priority).all()


@app.get("/students/{student_id}/schedule")
def get_student_schedule(student_id: int, db: Session = Depends(get_db)):
    _get_student_or_404(student_id, db)
    try:
        resp = httpx.get(
            f"{MANAGEMENT_SERVICE_URL}/schedule/student/{student_id}", timeout=10
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Management service unavailable") from exc
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="No schedule yet for this student")
    resp.raise_for_status()
    return resp.json()
