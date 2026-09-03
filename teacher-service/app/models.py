from sqlalchemy import Column, Integer, String, Text

from .database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    teacher_name = Column(String(120), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    capacity = Column(Integer, nullable=False)
