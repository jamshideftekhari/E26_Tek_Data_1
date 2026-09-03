from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import allocation, models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Management Service")


@app.post("/rooms", response_model=schemas.RoomOut)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = models.Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@app.get("/rooms", response_model=list[schemas.RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).all()


@app.post("/allocation/run", response_model=schemas.AllocationSummary)
def trigger_allocation(db: Session = Depends(get_db)):
    return allocation.run_allocation(db)


@app.get("/schedule", response_model=list[schemas.CourseScheduleOut])
def get_full_schedule(db: Session = Depends(get_db)):
    rows = db.query(models.Schedule).all()
    return [_schedule_with_students(row, db) for row in rows]


@app.get("/schedule/course/{course_id}", response_model=schemas.CourseScheduleOut)
def get_schedule_for_course(course_id: int, db: Session = Depends(get_db)):
    row = db.query(models.Schedule).filter(models.Schedule.course_id == course_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="No schedule for this course")
    return _schedule_with_students(row, db)


@app.get("/schedule/student/{student_id}", response_model=schemas.StudentScheduleOut)
def get_schedule_for_student(student_id: int, db: Session = Depends(get_db)):
    alloc = (
        db.query(models.Allocation)
        .filter(models.Allocation.student_id == student_id)
        .first()
    )
    if not alloc:
        raise HTTPException(status_code=404, detail="No schedule for this student")
    row = db.query(models.Schedule).filter(models.Schedule.id == alloc.schedule_id).first()
    return schemas.StudentScheduleOut(
        course_id=row.course_id, room_id=row.room_id, time_slot=row.time_slot
    )


@app.get("/priorities-summary", response_model=list[schemas.CoursePriorityDemand])
def get_priorities_summary():
    return allocation.priorities_summary()


def _schedule_with_students(row: models.Schedule, db: Session) -> schemas.CourseScheduleOut:
    student_ids = [
        a.student_id
        for a in db.query(models.Allocation)
        .filter(models.Allocation.schedule_id == row.id)
        .all()
    ]
    return schemas.CourseScheduleOut(
        course_id=row.course_id,
        room_id=row.room_id,
        time_slot=row.time_slot,
        student_ids=student_ids,
    )
