from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.submission import Submission


class SubmissionFile(SQLModel, table=True):
    __tablename__ = "submission_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="submissions.id")

    file_name: str
    file_url: str

    submission: Optional["Submission"] = Relationship(
        back_populates="files"
    )
