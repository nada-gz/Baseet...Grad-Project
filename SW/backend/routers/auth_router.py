from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from utils.auth import (
    hash_password, verify_password, create_access_token, 
    SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
)
from db.database import get_session
from sqlmodel import Session
from models.user import User, RoleEnum
from jose import jwt, JWTError
from schemas.user_schema import UserCreate, UserLogin, UserRead
from typing import List
from functools import wraps

router = APIRouter(
    prefix="/auth",
    tags=["Authentication & RBAC"]
)

# --- Helper to format user response ---
def user_response(user: User, db: Session = None) -> dict:
    """Format user response, optionally including studentId if user is a student"""
    response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value
    }
    
    # If user is a student, include studentId
    if user.role == RoleEnum.student and db:
        from models.student import Student
        student = db.query(Student).filter(Student.user_id == user.id).first()
        if student:
            response["studentId"] = student.id
    
    return response

# Note: get_current_user and oauth2_scheme are now imported from utils.auth

# --- Role decorator ---
def role_required(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role.value not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access forbidden for role '{current_user.role.value}'. Allowed roles: {allowed_roles}"
                )
            return func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# --- Auth endpoints ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_session)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    role = user.role if user.role else RoleEnum.student

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # If student, create student record
    student_id = None
    if role == RoleEnum.student:
        from models.student import Student
        student = Student(user_id=new_user.id)
        db.add(student)
        db.commit()
        db.refresh(student)
        student_id = student.id

    token = create_access_token(
        {"sub": new_user.email, "role": new_user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    user_data = user_response(new_user, db)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        {"sub": db_user.email, "role": db_user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response(db_user, db)
    }

@router.get("/me")
def read_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    """Get current user with studentId if applicable"""
    return user_response(current_user, db)
