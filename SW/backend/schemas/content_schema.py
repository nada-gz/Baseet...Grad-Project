from typing import Optional, List
from pydantic import BaseModel



class ContentMaterialRead(BaseModel):
    id: int
    lesson_id: int
    title: str
    file_url: str
    material_type: str

    class Config:
        orm_mode = True


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
