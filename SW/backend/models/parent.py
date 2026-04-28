from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .user import User
    from .student import Student

class Parent(SQLModel, table=True):
    __tablename__ = "parents"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # FK -> users.id
    user_id: int = Field(foreign_key="users.id")
    
    # Relationships
    user: "User" = Relationship(back_populates="parent")
    students: List["Student"] = Relationship(back_populates="parent")
