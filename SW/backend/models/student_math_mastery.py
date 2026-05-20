from typing import Optional
from sqlmodel import SQLModel, Field

class StudentMathMastery(SQLModel, table=True):
    __tablename__ = "student_math_mastery"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id", index=True)

    # Mastery probabilities (0.0 to 1.0)
    subitizing: float = Field(default=0.1)
    number_line: float = Field(default=0.1)
    place_value: float = Field(default=0.1)
    fact_retrieval: float = Field(default=0.1)
    word_problems: float = Field(default=0.1)

    # Tracking for difficulty down-scaling
    consecutive_errors: int = Field(default=0)
    current_node: str = Field(default="subitizing")
    last_updated: Optional[str] = None
