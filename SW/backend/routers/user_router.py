from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.user import User, RoleEnum
from schemas.user_schema import UserCreate, UserRead
from db.crud import add_user, get_all_users, get_user_by_username, get_user_by_id, update_user, delete_user
from routers.auth_router import get_current_user, role_required

router = APIRouter(prefix="/users", tags=["Users"])

# -----------------------------
# Create user (own account or student profile)
# -----------------------------
@router.post("/", response_model=UserRead)
def create_user_route(user: UserCreate, current_user: User = Depends(get_current_user)):
    # Only teacher/parent can create student profiles
    if user.role == RoleEnum.student and current_user.role in [RoleEnum.teacher, RoleEnum.parent]:
        return add_user(user.username, user.email, user.password, user.role)
    
    # Users can create their own accounts normally
    if user.role != RoleEnum.student and user.role == current_user.role:
        return add_user(user.username, user.email, user.password, user.role)

    raise HTTPException(status_code=403, detail="Not allowed to create this type of user")


# -----------------------------
# Get all users
# -----------------------------
@router.get("/", response_model=List[UserRead])
@role_required(["teacher", "parent", "supervisor"])
def get_users_route(current_user: User = Depends(get_current_user)):
    return get_all_users()


# -----------------------------
# Search user by username
# -----------------------------
@router.get("/search/{username}", response_model=UserRead)
@role_required(["teacher", "parent", "supervisor"])
def get_user_by_username_route(username: str, current_user: User = Depends(get_current_user)):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -----------------------------
# Get user by ID
# -----------------------------
@router.get("/{user_id}", response_model=UserRead)
@role_required(["teacher", "parent", "supervisor"])
def get_user_route(user_id: int, current_user: User = Depends(get_current_user)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -----------------------------
# Update student profile (teacher/parent only)
# -----------------------------
@router.put("/{user_id}", response_model=UserRead)
def update_user_route(user_id: int, username: str, email: str, current_user: User = Depends(get_current_user)):
    target_user = get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only teacher/parent can update student profiles
    if target_user.role != RoleEnum.student:
        raise HTTPException(status_code=403, detail="You can only update student profiles")
    
    if current_user.role not in [RoleEnum.teacher, RoleEnum.parent]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return update_user(user_id, username, email)


# -----------------------------
# Delete student profile (teacher/parent only)
# -----------------------------
@router.delete("/{user_id}")
def delete_user_route(user_id: int, current_user: User = Depends(get_current_user)):
    target_user = get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only teacher/parent can delete student profiles
    if target_user.role != RoleEnum.student:
        raise HTTPException(status_code=403, detail="You can only delete student profiles")
    
    if current_user.role not in [RoleEnum.teacher, RoleEnum.parent]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    delete_user(user_id)
    return {"deleted": user_id}