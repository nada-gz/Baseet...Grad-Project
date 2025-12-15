from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Milestone(SQLModel, table=True):
    __tablename__ = "milestones"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    student_id: int = Field(foreign_key="students.id")
    
    title: str  # e.g., "Milestone 1", "Introduction to Numbers"
    number: int  # e.g., 1, 2, 3 (for ordering)
    order: int  # Display order (can be same as number, but allows reordering)
    description: Optional[str] = None
    
    # Relationship to lessons
    lessons: list["Lesson"] = Relationship(back_populates="milestone")


from .lesson import Lesson

