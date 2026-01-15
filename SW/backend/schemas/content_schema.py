from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel



class ContentCourseRead(BaseModel):
    id: int
    course_number: int
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ContentCourseCreate(BaseModel):
    course_number: int
    description: Optional[str] = None


class ContentMaterialRead(BaseModel):
    id: int
    lesson_id: int
    title: str
    file_url: str
    material_type: str

    class Config:
        from_attributes = True

class StudentReadWithUser(BaseModel):
    id: int
    user_id: int
    course_number: Optional[int]
    username: str
    email: str
    age: Optional[int]
    classroom_id: Optional[int] = None
    classroom_name: Optional[str] = None
    level_name: Optional[str] = None
    status: Optional[str] = "Active"
    online: bool = False
    last_access: Optional[datetime] = None
    state: Optional[str] = "Relaxed"



class ContentLessonRead(BaseModel):
    id: int
    course_number: int
    milestone_number: int
    lesson_number: int
    title: str
    description: Optional[str] = None
    materials: List[ContentMaterialRead] = []

    class Config:
        from_attributes = True


class ContentLessonCreate(BaseModel):
    course_number: int
    milestone_number: int
    lesson_number: int
    title: str
