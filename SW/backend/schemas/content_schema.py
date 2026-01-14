from typing import Optional, List
from pydantic import BaseModel



class ContentLevelRead(BaseModel):
    id: int
    level_number: int
    description: Optional[str] = None

    class Config:
        orm_mode = True

class ContentLevelCreate(BaseModel):
    level_number: int
    description: Optional[str] = None


class ContentMaterialRead(BaseModel):
    id: int
    lesson_id: int
    title: str
    file_url: str
    material_type: str

    class Config:
        orm_mode = True

class StudentReadWithUser(BaseModel):
    id: int
    user_id: int
    level_number: Optional[int]
    username: str
    email: str
    age: Optional[int]



class ContentLessonRead(BaseModel):
    id: int
    level_number: int
    milestone_number: int
    lesson_number: int
    title: str
    description: Optional[str] = None
    materials: List[ContentMaterialRead] = []

    class Config:
        orm_mode = True


class ContentLessonCreate(BaseModel):
    level_number: int
    milestone_number: int
    lesson_number: int
    title: str
