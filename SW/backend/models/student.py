from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship


class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: Optional[int] = Field(default=None, primary_key=True)

    # FK → users.id
    user_id: int = Field(foreign_key="users.id")

    age: Optional[int] = None
    autism_type: Optional[str] = None
    sensitivities: Optional[str] = None  # or JSON if using PostgreSQL (later)
    learning_style: Optional[str] = None
    baseline_engagement: Optional[float] = None
    course_number: Optional[int] = None

    classroom_id: Optional[int] = Field(default=None, foreign_key="classrooms.id")
    classroom: Optional["Classroom"] = Relationship(back_populates="students")

    # Parent relationship
    parent_id: Optional[int] = Field(default=None, foreign_key="parents.id")
    parent: Optional["Parent"] = Relationship(back_populates="students")

    # Preferences
    difficulty_level: int = Field(default=5)  # 1-10
    sensory_settings: Optional[str] = Field(default="{}") # JSON string for now

    # Relationship to User
    user: "User" = Relationship(back_populates="student")



from .user import User
if TYPE_CHECKING:
    from models.classroom import Classroom
    from models.parent import Parent