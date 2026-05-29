from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class ParentNotification(SQLModel, table=True):
    __tablename__ = "parent_notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = Field(foreign_key="parents.id")
    
    title: str
    message: str
    type: str  # e.g., 'alert', 'comment', 'feedback'
    
    is_read: bool = Field(default=False)
    is_urgent: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
