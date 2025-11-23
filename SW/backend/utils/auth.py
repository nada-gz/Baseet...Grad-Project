from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "3vhr76INTMRMP6hWn89OE1LfK6N1ux6eCJrxQAwG7es"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _truncate_password(password: str, max_bytes: int = 72) -> str:
    """Truncate password to ensure UTF-8 encoding is <= max_bytes."""
    # Simple approach: keep removing characters until encoded length <= max_bytes
    truncated = password
    while len(truncated.encode('utf-8')) > max_bytes:
        truncated = truncated[:-1]
        if not truncated:  # Safety check
            break
    return truncated

def hash_password(password: str) -> str:
    # Bcrypt has a 72-byte limit, so we need to truncate by bytes, not characters
    truncated = _truncate_password(password, 72)
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Bcrypt has a 72-byte limit, so we need to truncate by bytes, not characters
    truncated = _truncate_password(plain_password, 72)
    return pwd_context.verify(truncated, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 
