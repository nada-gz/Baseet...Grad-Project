from typing import Optional, List
from pydantic import BaseModel


class MilestoneCreate(BaseModel):
    student_id: int
    title: str
    number: int
    order: Optional[int] = None  # If not provided, uses number
    description: Optional[str] = None


class MilestoneRead(BaseModel):
    id: int
    student_id: int
    title: str
    number: int
    order: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    number: Optional[int] = None
    order: Optional[int] = None
    description: Optional[str] = None


class MilestoneWithLessons(MilestoneRead):
    """Milestone with its lessons included"""
    lessons: List["LessonRead"] = []

    class Config:
        from_attributes = True


# Import here to avoid circular dependency
from .lesson_schema import LessonRead
MilestoneWithLessons.model_rebuild()

