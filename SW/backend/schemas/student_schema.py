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
        from_attributes = True


class StudentUpdate(BaseModel):
    age: Optional[int] = None
    autism_type: Optional[str] = None
    sensitivities: Optional[str] = None
    learning_style: Optional[str] = None
    baseline_engagement: Optional[float] = None


class StudentProfileDetail(BaseModel):
    id: int
    user_id: int
    username: str
    email: str
    role: str
    age: Optional[int] = None
    autism_type: Optional[str] = None
    sensitivities: Optional[str] = None
    learning_style: Optional[str] = None
    baseline_engagement: Optional[float] = None
    classroom_name: Optional[str] = None
    level_name: Optional[str] = None
    is_flagged: bool = False
    online: bool = False

    class Config:
        from_attributes = True
