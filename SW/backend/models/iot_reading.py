from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class IOTReading(SQLModel, table=True):
    __tablename__ = "iot_readings"

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: Optional[int] = Field(default=None, foreign_key="students.id")
    heart_rate: float
    gsr: float
    temperature: float
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
