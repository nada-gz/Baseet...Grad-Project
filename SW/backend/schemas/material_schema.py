from typing import Optional
from pydantic import BaseModel


class MaterialCreate(BaseModel):
    student_id: int
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    lesson_id: Optional[int] = None


class MaterialRead(BaseModel):
    id: int
    student_id: int
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    lesson_id: Optional[int] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    lesson_id: Optional[int] = None

