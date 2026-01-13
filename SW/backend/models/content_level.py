from typing import Optional
from sqlmodel import SQLModel, Field

class ContentLevel(SQLModel, table=True):
    __tablename__ = "content_levels"

    id: Optional[int] = Field(default=None, primary_key=True)
    level_number: int = Field(index=True, unique=True)
    description: Optional[str] = None
