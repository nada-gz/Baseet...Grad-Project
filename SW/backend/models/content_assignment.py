from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.content_lesson import ContentLesson
    from models.content_assignment_file import ContentAssignmentFile

class ContentAssignment(SQLModel, table=True):
    __tablename__ = "content_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="content_lessons.id")
    
    title: str
    description: Optional[str] = None
    assignment_type: str = "unknown"
    file_url: str = "" # Keeping for legacy, though new code will use files relationship

    lesson: Optional["ContentLesson"] = Relationship(back_populates="assignments")
    files: List["ContentAssignmentFile"] = Relationship(back_populates="assignment")
