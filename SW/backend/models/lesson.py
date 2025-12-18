from typing import Optional
from sqlmodel import SQLModel, Field

class Lesson(SQLModel, table=True):
    __tablename__ = "lessons"

    id: Optional[int] = Field(default=None, primary_key=True)

    student_id: int = Field(foreign_key="students.id")
    milestone_id: Optional[int] = Field(default=None, foreign_key="milestones.id")

    title: str
    number: str              # e.g. "3.1"
    progress: int = 0        # 0 → 100
    status: str              # locked | in-progress | completed
    description: Optional[str] = None   # optional lesson description
