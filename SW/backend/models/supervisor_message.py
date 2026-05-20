from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class SupervisorMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supervisor_id: int = Field(foreign_key="users.id")
    teacher_id: int = Field(foreign_key="users.id")
    student_id: int = Field(foreign_key="students.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = Field(default=False)

    # Relationships
    student: "Student" = Relationship()

if TYPE_CHECKING:
    from .student import Student
