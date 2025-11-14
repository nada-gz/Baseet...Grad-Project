from fastapi import APIRouter, HTTPException
from ..db.crud import add_user, get_all_users, get_user_by_name, get_user_by_id, update_user, delete_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
def create_user_route(name: str, age: int):
    return add_user(name, age)

@router.get("/")
def get_users_route():
    return get_all_users()

@router.get("/search/{name}")
def get_user_by_name_route(name: str):
    user = get_user_by_name(name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}")
def get_user_route(user_id: int):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}")
def update_user_route(user_id: int, name: str, age: int):
    user = update_user(user_id, name, age)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user_route(user_id: int):
    user = delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": user_id}
