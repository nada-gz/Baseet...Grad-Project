from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from db.database import get_session
from models.user import User, RoleEnum
from models.student import Student
from models.student_flag import StudentFlag
from models.teacher_student_link import TeacherStudentLink
from models.supervisor_report import SupervisorReport
from models.supervisor_message import SupervisorMessage
from utils.dependencies import require_role
from schemas.supervisor_schema import (
    StudentFlagRead, TeacherWithLoad, AssignStudentsToTeacherRequest,
    ResolveFlagRequest, SupervisorReportCreate
)
from pydantic import BaseModel

class SupervisorMessageCreate(BaseModel):
    teacher_id: int
    student_id: int
    content: str
from schemas.content_schema import StudentReadWithUser

router = APIRouter(prefix="/supervisor", tags=["Supervisor"])

# -----------------------
# Student Monitoring
# -----------------------

from models.classroom import Classroom
from models.class_level import ClassLevel

@router.get("/students/all", response_model=List[StudentReadWithUser])
def get_all_students_for_supervisor(session: Session = Depends(get_session), current_user: User = Depends(require_role(["supervisor"]))):
    try:
        # Simplified query to ensure it returns data even if some links are missing
        students = session.exec(select(Student)).all()
        result = []
        for s in students:
            u = session.get(User, s.user_id)
            if not u: continue
            
            cl = session.get(Classroom, s.classroom_id) if s.classroom_id else None
            lvl = session.get(ClassLevel, cl.level_id) if (cl and cl.level_id) else None
            
            result.append(StudentReadWithUser(
                id=s.id,
                user_id=s.user_id,
                username=u.username,
                email=u.email,
                age=s.age,
                is_flagged=s.is_flagged,
                online=(s.id % 2 == 0),
                status="Active",
                classroom_id=s.classroom_id,
                classroom_name=cl.name if cl else None,
                level_name=lvl.name if lvl else None
            ))
        return result
    except Exception as e:
        print(f"Error in get_all_students_for_supervisor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students/flagged", response_model=List[StudentFlagRead])
def get_flagged_students(session: Session = Depends(get_session), current_user: User = Depends(require_role(["supervisor"]))):
    statement = select(StudentFlag).where(StudentFlag.status != "resolved")
    flags = session.exec(statement).all()
    
    # We might need to populate student info manually if relationship is not eager
    return flags

@router.post("/flags/{flag_id}/resolve")
def resolve_student_flag(
    flag_id: int, 
    req: ResolveFlagRequest,
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_role(["supervisor"]))
):
    flag = session.get(StudentFlag, flag_id)
    if not flag:
        raise HTTPException(404, "Flag not found")
    
    flag.status = req.status
    flag.supervisor_notes = req.notes
    flag.supervisor_id = current_user.id
    if req.status == "resolved":
        flag.resolved_at = datetime.utcnow()
        
        # Check if there are other active flags for this student
        other_flags = session.exec(select(StudentFlag).where(
            StudentFlag.student_id == flag.student_id,
            StudentFlag.status != "resolved",
            StudentFlag.id != flag_id
        )).first()
        
        if not other_flags:
            student = session.get(Student, flag.student_id)
            if student:
                student.is_flagged = False
                session.add(student)
                
    session.add(flag)
    session.commit()
    return {"ok": True}

# -----------------------
# Teacher Management
# -----------------------

@router.get("/teachers", response_model=List[TeacherWithLoad])
def get_teachers_with_load(session: Session = Depends(get_session), current_user: User = Depends(require_role(["supervisor"]))):
    statement = select(User).where(User.role == RoleEnum.teacher)
    teachers = session.exec(statement).all()
    
    result = []
    for t in teachers:
        links = session.exec(select(TeacherStudentLink).where(TeacherStudentLink.teacher_id == t.id)).all()
        student_ids = [link.student_id for link in links]
        result.append(TeacherWithLoad(
            id=t.id,
            username=t.username,
            email=t.email,
            assigned_students_count=len(student_ids),
            assigned_student_ids=student_ids
        ))
    return result

@router.post("/assignments")
def assign_students_to_teacher(
    req: AssignStudentsToTeacherRequest,
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_role(["supervisor"]))
):
    # Clear existing if needed? Or just add new ones. 
    # Usually we add new ones. 
    for s_id in req.student_ids:
        # Check if already assigned
        existing = session.get(TeacherStudentLink, {"teacher_id": req.teacher_id, "student_id": s_id})
        if not existing:
            link = TeacherStudentLink(teacher_id=req.teacher_id, student_id=s_id)
            session.add(link)
    
    session.commit()
    return {"ok": True}

@router.delete("/assignments")
def unassign_students_from_teacher(
    req: AssignStudentsToTeacherRequest,
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_role(["supervisor"]))
):
    for s_id in req.student_ids:
        link = session.get(TeacherStudentLink, {"teacher_id": req.teacher_id, "student_id": s_id})
        if link:
            session.delete(link)
    
    session.commit()
    return {"ok": True}

# -----------------------
# Reports
# -----------------------

@router.post("/reports")
def create_supervisor_report(
    req: SupervisorReportCreate,
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_role(["supervisor"]))
):
    report = SupervisorReport(
        student_id=req.student_id,
        supervisor_id=current_user.id,
        title=req.title,
        content=req.content
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return report

# -----------------------
# Messaging
# -----------------------

@router.post("/messages")
def send_message_to_teacher(
    req: SupervisorMessageCreate,
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_role(["supervisor"]))
):
    msg = SupervisorMessage(
        supervisor_id=current_user.id,
        teacher_id=req.teacher_id,
        student_id=req.student_id,
        content=req.content
    )
    session.add(msg)
    session.commit()
    return {"ok": True}
