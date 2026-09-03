from sqlalchemy import Column, ForeignKey, Integer, String

from .database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    capacity = Column(Integer, nullable=False)
    time_slot = Column(String(50), nullable=False)


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, nullable=False)  # logical FK -> course_db.courses.id
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    time_slot = Column(String(50), nullable=False)


class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedule.id"), nullable=False)
    student_id = Column(Integer, nullable=False)  # logical FK -> student_db.students.id
