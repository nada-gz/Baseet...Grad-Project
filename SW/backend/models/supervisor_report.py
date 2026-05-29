from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class SupervisorReport(SQLModel, table=True):
    __tablename__ = "supervisor_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    supervisor_id: int = Field(foreign_key="users.id")
    
    title: str
    content: str  # Can store JSON or Markdown
    
    # Optional PDF link if generated
    file_url: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: "Student" = Relationship()
    supervisor: "User" = Relationship()

from .student import Student
from .user import User
