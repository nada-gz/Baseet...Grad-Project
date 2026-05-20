from typing import List, Optional
from pydantic import BaseModel
from schemas.content_schema import ContentCourseRead, StudentReadWithUser

class ClassroomBase(BaseModel):
    name: str

class ClassroomCreate(ClassroomBase):
    level_id: int

class ClassroomRead(ClassroomBase):
    id: int
    level_id: int
    
    # Optional nested data
    courses: List[ContentCourseRead] = []
    # Students might be too heavy to include by default, but we can if needed
    student_count: int = 0 

    class Config:
        from_attributes = True

class ClassLevelBase(BaseModel):
    name: str

class ClassLevelCreate(ClassLevelBase):
    pass

class ClassLevelRead(ClassLevelBase):
    id: int
    classrooms: List[ClassroomRead] = []

    class Config:
        from_attributes = True

class AssignStudentsRequest(BaseModel):
    student_ids: List[int]

class AssignCoursesRequest(BaseModel):
    course_ids: List[int]
