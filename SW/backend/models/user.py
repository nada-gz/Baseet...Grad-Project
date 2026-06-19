from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column
import sqlalchemy as sa
from .teacher_student_link import TeacherStudentLink


class RoleEnum(str, Enum):
    teacher = "teacher"
    parent = "parent"
    student = "student"
    supervisor = "supervisor"
    admin = "admin"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role: RoleEnum = Field(default=RoleEnum.student)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Password reset fields
    reset_token: Optional[str] = Field(default=None, sa_column=Column(sa.String, nullable=True))
    reset_token_expires: Optional[datetime] = Field(default=None, sa_column=Column(sa.DateTime, nullable=True))

    student: Optional["Student"] = Relationship(back_populates="user")
    parent: Optional["Parent"] = Relationship(back_populates="user")

    # For Teachers: list of assigned students
    assigned_students: List["Student"] = Relationship(back_populates="teachers", link_model=TeacherStudentLink)

from .student import Student
from .parent import Parent