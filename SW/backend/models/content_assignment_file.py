from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.content_assignment import ContentAssignment

class ContentAssignmentFile(SQLModel, table=True):
    __tablename__ = "content_assignment_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    assignment_id: int = Field(foreign_key="content_assignments.id")
    
    file_url: str
    file_name: str

    assignment: Optional["ContentAssignment"] = Relationship(back_populates="files")
