from fastapi import APIRouter, Depends
from models.user import User
from utils.dependencies import require_role

router = APIRouter(prefix="/auth/dashboard", tags=["Dashboard"])

@router.get("/teacher")
def teacher_dashboard(user: User = Depends(require_role(["teacher"]))):
    return {"message": "Teacher access granted", "user": {"email": user.email, "role": user.current_role}}

@router.get("/student")
def student_dashboard(user: User = Depends(require_role(["student"]))):
    return {"message": "Student access granted", "user": {"email": user.email, "role": user.current_role}}

@router.get("/parent")
def parent_dashboard(user: User = Depends(require_role(["parent"]))):
    return {"message": "Parent access granted", "user": {"email": user.email, "role": user.current_role}}

@router.get("/supervisor")
def supervisor_dashboard(user: User = Depends(require_role(["supervisor"]))):
    return {"message": "Supervisor access granted", "user": {"email": user.email, "role": user.current_role}}
