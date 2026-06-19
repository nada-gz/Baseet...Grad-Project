from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from models.user import RoleEnum
import re

PASSWORD_RULES = [
    (r'.{8,}',             "at least 8 characters"),
    (r'[A-Z]',             "at least one uppercase letter"),
    (r'[a-z]',             "at least one lowercase letter"),
    (r'[0-9]',             "at least one number"),
    (r'[!@#$%^&*(),.?\":{}|<>_\-]', "at least one special character"),
]

def validate_password_strength(password: str) -> str:
    errors = [msg for pattern, msg in PASSWORD_RULES if not re.search(pattern, password)]
    if errors:
        raise ValueError("Password must contain: " + ", ".join(errors))
    return password

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.student

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return validate_password_strength(v)

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