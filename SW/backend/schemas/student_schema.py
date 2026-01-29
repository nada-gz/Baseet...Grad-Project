from typing import Optional
from pydantic import BaseModel


class StudentCreate(BaseModel):
    user_id: int
    age: Optional[int] = None
    autism_type: Optional[str] = None
    sensitivities: Optional[str] = None  # PostgreSQL..? JSON (later)
    learning_style: Optional[str] = None
    baseline_engagement: Optional[float] = None


class StudentRead(BaseModel):
    id: int
    user_id: int
    age: Optional[int] = None
    autism_type: Optional[str] = None
    sensitivities: Optional[str] = None
    learning_style: Optional[str] = None
    baseline_engagement: Optional[float] = None

    class Config:
        from_attributes = True  # Allows returning SQLModel objects directly


class StudentUpdate(BaseModel):
    age: Optional[int] = None
    autism_type: Optional[str] = None
    sensitivities: Optional[str] = None
    learning_style: Optional[str] = None
    baseline_engagement: Optional[float] = None
