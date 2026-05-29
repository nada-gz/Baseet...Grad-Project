from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from schemas.content_schema import StudentReadWithUser

class StudentFlagRead(BaseModel):
    id: int
    student_id: int
    source: str
    reason: str
    status: str
    created_at: datetime
    supervisor_notes: Optional[str] = None
    student: Optional[StudentReadWithUser] = None

    class Config:
        from_attributes = True

class TeacherWithLoad(BaseModel):
    id: int
    username: str
    email: str
    assigned_students_count: int
    assigned_student_ids: List[int] = []

    class Config:
        from_attributes = True

class AssignStudentsToTeacherRequest(BaseModel):
    teacher_id: int
    student_ids: List[int]

class ResolveFlagRequest(BaseModel):
    notes: str
    status: str = "resolved" # or "investigated"

class SupervisorReportCreate(BaseModel):
    student_id: int
    title: str
    content: str
