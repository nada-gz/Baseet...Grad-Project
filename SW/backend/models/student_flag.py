from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class StudentFlag(SQLModel, table=True):
    __tablename__ = "student_flags"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    
    # "teacher", "iot", "ai_face"
    source: str 
    reason: str
    
    # "active", "investigated", "resolved"
    status: str = Field(default="active")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    supervisor_id: Optional[int] = Field(default=None, foreign_key="users.id")
    supervisor_notes: Optional[str] = None

    # Relationships
    student: "Student" = Relationship(back_populates="flags")

from .student import Student
