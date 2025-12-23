from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel


class SubmissionFileRead(SQLModel):
    file_name: str
    file_url: str


class FeedbackRead(SQLModel):
    comment: str
    rating: Optional[int]


class SubmissionRead(SQLModel):
    id: int
    description: Optional[str]
    submitted_at: datetime
    updated_at: Optional[datetime]

    files: List[SubmissionFileRead]
    feedback: Optional[FeedbackRead]
