from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.assignment import Assignment
    from models.feedback import Feedback
    from models.submission_file import SubmissionFile


class Submission(SQLModel, table=True):
    __tablename__ = "submissions"

    id: Optional[int] = Field(default=None, primary_key=True)

    assignment_id: int = Field(foreign_key="assignments.id")
    student_id: int = Field(foreign_key="students.id")

    description: Optional[str] = None

    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    submission_method: Optional[str] = Field(default="typed") # 'typed', 'voice', 'upload'
    story_grammar_score: Optional[str] = None # e.g. "C,S,P"
    causal_connective_count: Optional[int] = Field(default=0)
    audio_url: Optional[str] = None

    assignment: Optional["Assignment"] = Relationship(back_populates="submissions")

    # ✅ ONE-TO-ONE
    feedback: Optional["Feedback"] = Relationship(
        back_populates="submission",
        sa_relationship_kwargs={"uselist": False}
    )

    # ✅ ONE-TO-MANY (files)
    files: List["SubmissionFile"] = Relationship(
        back_populates="submission",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
