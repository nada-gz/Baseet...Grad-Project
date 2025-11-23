from pydantic import BaseModel, EmailStr
from typing import Optional
from models.user import RoleEnum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.student

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum

    class Config:
        from_attributes = True  # Updated for Pydantic V2