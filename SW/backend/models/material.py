from typing import Optional
from sqlmodel import SQLModel, Field


class Material(SQLModel, table=True):
    __tablename__ = "materials"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None  # URL or path to the material file
    file_type: Optional[str] = None  # pdf, video, image, etc.
    lesson_id: Optional[int] = None  # Optional link to a specific lesson
    created_at: Optional[str] = None  # ISO format datetime string

