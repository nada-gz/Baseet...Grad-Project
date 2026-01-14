from typing import Optional
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
    level_number: Optional[int] = None

    # Relationship to User
    user: "User" = Relationship(back_populates="student")



from .user import User