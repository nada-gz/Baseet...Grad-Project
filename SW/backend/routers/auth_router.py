from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from utils.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from db.database import get_session
from sqlmodel import Session
from models.user import User, RoleEnum
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError
from schemas.user_schema import UserCreate, UserLogin, UserRead
from typing import List
from functools import wraps

router = APIRouter(
    prefix="/auth",
    tags=["Authentication & RBAC"]
)

# --- Helper to format user response ---
def user_response(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value
    }

# --- Auth scheme ---
oauth2_scheme = APIKeyHeader(name="Authorization", scheme_name="JWT")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid format. Expected: Bearer <token>")
    jwt_token = token.split(" ")[1]
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

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
    role = RoleEnum(user.role) if user.role else RoleEnum.student

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        {"sub": new_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response(new_user)
    }

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        {"sub": db_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_response(db_user)
    }

@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Standardized dashboard endpoints ---
@router.get("/dashboard/teacher")
@role_required(["teacher"])
def dashboard_teacher(current_user: User):
    return {"message": "Teacher access granted", "user": user_response(current_user)}

@router.get("/dashboard/student")
@role_required(["student"])
def dashboard_student(current_user: User):
    return {"message": "Student access granted", "user": user_response(current_user)}

@router.get("/dashboard/parent")
@role_required(["parent"])
def dashboard_parent(current_user: User):
    return {"message": "Parent access granted", "user": user_response(current_user)}

@router.get("/dashboard/supervisor")
@role_required(["supervisor"])
def dashboard_supervisor(current_user: User):
    return {"message": "Supervisor access granted", "user": user_response(current_user)}

