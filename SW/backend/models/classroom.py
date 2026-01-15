from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.class_level import ClassLevel
    from models.student import Student
    from models.content_course import ContentCourse

# Link table for Many-to-Many between Classroom and ContentCourse
class ClassroomCourseLink(SQLModel, table=True):
    __tablename__ = "classroom_course_links"
    
    classroom_id: Optional[int] = Field(default=None, foreign_key="classrooms.id", primary_key=True)
    course_id: Optional[int] = Field(default=None, foreign_key="content_courses.id", primary_key=True)

class Classroom(SQLModel, table=True):
    __tablename__ = "classrooms"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str # e.g. "Class A"
    
    level_id: int = Field(foreign_key="class_levels.id")
    
    level: "ClassLevel" = Relationship(back_populates="classrooms")
    students: List["Student"] = Relationship(back_populates="classroom")
    
    courses: List["ContentCourse"] = Relationship(link_model=ClassroomCourseLink)
