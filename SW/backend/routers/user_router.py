from fastapi import APIRouter, HTTPException
from db.crud import add_user, get_all_users, get_user_by_username, get_user_by_id, update_user, delete_user
from models.user import RoleEnum
from schemas.user_schema import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
def create_user_route(user: UserCreate):
    return add_user(user.username, user.email, user.password, user.role)

@router.get("/", response_model=list[UserRead])
def get_users_route():
    return get_all_users()

@router.get("/search/{username}")
def get_user_by_username_route(username: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}", response_model=UserRead)
def get_user_route(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
def update_user_route(user_id: int, username: str, email: str):
    user = update_user(user_id, username, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user_route(user_id: int):
    user = delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": user_id}
