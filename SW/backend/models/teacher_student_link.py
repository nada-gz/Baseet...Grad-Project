from typing import Optional
from sqlmodel import SQLModel, Field

class TeacherStudentLink(SQLModel, table=True):
    __tablename__ = "teacher_student_links"

    teacher_id: int = Field(foreign_key="users.id", primary_key=True)
    student_id: int = Field(foreign_key="students.id", primary_key=True)
