from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import json
from models.user import User
from models.student import Student
from models.parent import Parent
from utils.dependencies import require_role
from db.database import get_session
from sqlmodel import Session
from services.ai.report import generate_baseet_report, get_telemetry_for_student

router = APIRouter(prefix="/auth/dashboard", tags=["Dashboard"])


@router.get("/student")
def student_dashboard(
    user: User = Depends(require_role(["student"])),
    db: Session = Depends(get_session)
):
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found for this user.")
        
    try:
        telemetry = get_telemetry_for_student(student.id, db)
        report_str = generate_baseet_report("student", telemetry)
        return json.loads(report_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate student report: {str(e)}")


@router.get("/teacher")
def teacher_dashboard(
    student_id: Optional[int] = None,
    user: User = Depends(require_role(["teacher"])),
    db: Session = Depends(get_session)
):
    if student_id is not None:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found.")
    else:
        student = user.assigned_students[0] if user.assigned_students else None
        if not student:
            student = db.query(Student).first()
            if not student:
                raise HTTPException(status_code=404, detail="No students found in the database.")

    try:
        telemetry = get_telemetry_for_student(student.id, db)
        report_str = generate_baseet_report("teacher", telemetry)
        return json.loads(report_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate teacher report: {str(e)}")


@router.get("/parent")
def parent_dashboard(
    student_id: Optional[int] = None,
    user: User = Depends(require_role(["parent"])),
    db: Session = Depends(get_session)
):
    parent = db.query(Parent).filter(Parent.user_id == user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent record not found for this user.")

    if student_id is not None:
        student = db.query(Student).filter(Student.id == student_id, Student.parent_id == parent.id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Child student with ID {student_id} not found for this parent.")
    else:
        student = parent.students[0] if parent.students else None
        if not student:
            raise HTTPException(status_code=404, detail="No linked child student found for this parent.")

    try:
        telemetry = get_telemetry_for_student(student.id, db)
        report_str = generate_baseet_report("parent", telemetry)
        return json.loads(report_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate parent report: {str(e)}")


@router.get("/supervisor")
def supervisor_dashboard(
    student_id: Optional[int] = None,
    user: User = Depends(require_role(["supervisor"])),
    db: Session = Depends(get_session)
):
    if student_id is not None:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found.")
    else:
        student = db.query(Student).first()
        if not student:
            raise HTTPException(status_code=404, detail="No students exist in the system to calculate telemetry.")
        
    try:
        telemetry = get_telemetry_for_student(student.id, db)
        report_str = generate_baseet_report("supervisor", telemetry)
        return json.loads(report_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate supervisor report: {str(e)}")

