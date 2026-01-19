from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel


class AssignmentBase(SQLModel):
    title: str
    description: Optional[str] = None
    assignment_type: str
    file_url: str
    deadline: Optional[datetime] = None


class AssignmentCreate(AssignmentBase):
    lesson_id: int


class AssignmentRead(AssignmentBase):
    id: int
    lesson_id: int
