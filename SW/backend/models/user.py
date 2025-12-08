from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    role: str = Field(default="student")  # Role: student, teacher, parent, supervisor
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # One-to-one relationship
    student: Optional["Student"] = Relationship(back_populates="user")

from .student import Student