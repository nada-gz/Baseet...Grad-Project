from fastapi import Depends, HTTPException, status
from models.user import User

from utils.auth import get_current_user

def require_role(allowed_roles: list[str]):
    """
    Dependency to restrict access based on allowed roles.
    Uses user.current_role (from token) instead of DB role.
    """
    def role_checker(user: User = Depends(get_current_user)):
        role_to_check = getattr(user, "current_role", user.role.value)
        if role_to_check not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden for role '{role_to_check}'. Allowed roles: {allowed_roles}"
            )
        return user
    return role_checker
