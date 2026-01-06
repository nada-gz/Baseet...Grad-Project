from typing import Optional, TYPE_CHECKING, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from models.lesson import Lesson

class Log(SQLModel, table=True):
    __tablename__ = "log_table"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_input: Optional[str] = None
    intent: Optional[str] = None
    topic: Optional[str] = None
    question: Optional[str] = None
    correct: Optional[bool] = None
    correct_answer: Optional[str] = None
    user_choice: Optional[str] = None
    topic_id: Optional[int] = Field(foreign_key="lessons.id")

    # Relationship to Lesson
    lesson: Optional["Lesson"] = Relationship(back_populates="logs")
