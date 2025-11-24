from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from utils.auth import hash_password, verify_password, create_access_token
from db.database import get_session
from sqlmodel import Session
from models.user import User, RoleEnum
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError
from utils.auth import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.user_schema import UserCreate, UserLogin, UserRead


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_session)):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed = hash_password(user.password)
        # Use role from request, default to student if not provided
        user_role = user.role if user.role else RoleEnum.student
        new_user = User(username=user.username, email=user.email, hashed_password=hashed, role=user_role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Auto-login after registration - return token and role
        token = create_access_token({"sub": new_user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {
            "message": "User registered successfully",
            "access_token": token,
            "token_type": "bearer",
            "role": new_user.role.value if new_user.role else "student"
        }
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Return role for frontend to store
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role.value if db_user.role else "student"
    }

oauth2_scheme = APIKeyHeader(
    name="Authorization",
    scheme_name="JWT"
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format. Expected 'Bearer <token>'.")

    token = token.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
