from typing import Optional
from sqlmodel import SQLModel, Field

class Course(SQLModel, table=True):
    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    subject: str = Field(default="Generic")
    description: Optional[str] = None
    image_url: Optional[str] = None
