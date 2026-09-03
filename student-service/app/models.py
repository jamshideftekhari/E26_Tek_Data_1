from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    priorities = relationship(
        "Priority", back_populates="student", order_by="Priority.rank"
    )


class Priority(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, nullable=False)  # logical FK -> course_db.courses.id
    rank = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="priorities")
