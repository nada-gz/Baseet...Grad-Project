from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from db.database import get_session
from models.user import User, RoleEnum

load_dotenv()

SECRET_KEY = "3vhr76INTMRMP6hWn89OE1LfK6N1ux6eCJrxQAwG7es"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Auth scheme ---
oauth2_scheme = APIKeyHeader(name="Authorization", scheme_name="JWT")

# ----------------------------
# Password utils
# ----------------------------
def _truncate_password(password: str, max_bytes: int = 72) -> str:
    truncated = password
    while len(truncated.encode("utf-8")) > max_bytes:
        truncated = truncated[:-1]
        if not truncated:
            break
    return truncated

def hash_password(password: str) -> str:
    truncated = _truncate_password(password, 72)
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = _truncate_password(plain_password, 72)
    return pwd_context.verify(truncated, hashed_password)

# ----------------------------
# JWT utils
# ----------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ----------------------------
# Get current user from token
# ----------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """
    Decode JWT token, fetch user from DB, attach current role from token.
    Expects format: "Bearer <token>"
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing")
    
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format. Expected: Bearer <token>")
    
    jwt_token = token.split(" ")[1]
    
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
