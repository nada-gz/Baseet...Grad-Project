from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship

class LinkingCode(SQLModel, table=True):
    __tablename__ = "linking_codes"
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    code: str = Field(index=True, unique=True)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    is_used: bool = Field(default=False)

class StudentReport(SQLModel, table=True):
    __tablename__ = "student_reports"
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    report_date: date = Field(default_factory=date.today)
    
    # The JSON data provided by the reporting agent
    report_data: str = Field(default="{}") 
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
