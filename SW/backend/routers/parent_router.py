from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from db.database import get_session
from models.user import User, RoleEnum
from models.student import Student
from models.parent import Parent
from models.parent_notification import ParentNotification
from models.parent_extensions import LinkingCode, StudentReport
from utils.auth import get_current_user
from datetime import datetime, timedelta
import random
import json

router = APIRouter(prefix="/parent", tags=["Parent Dashboard"])

@router.get("/my-children")
def get_my_children(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if current_user.role != RoleEnum.parent:
        raise HTTPException(status_code=403, detail="Only parents can access this")
    
    parent = db.exec(select(Parent).where(Parent.user_id == current_user.id)).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent record not found")
    
    children = db.exec(select(Student).where(Student.parent_id == parent.id)).all()
    
    result = []
    for child in children:
        child_user = db.get(User, child.user_id)
        result.append({
            "id": child.id,
            "name": child_user.username if child_user else "Unknown",
            "age": child.age,
            "autism_type": child.autism_type,
            "difficulty_level": child.difficulty_level,
            "sensory_settings": json.loads(child.sensory_settings) if child.sensory_settings else {}
        })
    return result

@router.post("/link-child")
def link_child(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if current_user.role != RoleEnum.parent:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify code
    link_record = db.exec(
        select(LinkingCode)
        .where(LinkingCode.code == code, LinkingCode.is_used == False)
    ).first()
    
    if not link_record:
        raise HTTPException(status_code=400, detail="Invalid or already used link code")
    
    if link_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Link code has expired")
    
    parent = db.exec(select(Parent).where(Parent.user_id == current_user.id)).first()
    if not parent:
        # Auto-create parent record if it's missing but user has the role
        parent = Parent(user_id=current_user.id)
        db.add(parent)
        db.commit()
        db.refresh(parent)

    student = db.get(Student, link_record.student_id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    student.parent_id = parent.id
    link_record.is_used = True
    
    db.add(student)
    db.add(link_record)
    db.commit()
    
    student_user = db.get(User, student.user_id)
    return {"message": f"Successfully linked to {student_user.username if student_user else 'child'}"}

@router.get("/notifications", response_model=List[ParentNotification])
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    parent = db.exec(select(Parent).where(Parent.user_id == current_user.id)).first()
    if not parent:
        return []
    
    notifications = db.exec(
        select(ParentNotification)
        .where(ParentNotification.parent_id == parent.id)
        .order_by(ParentNotification.created_at.desc())
    ).all()
    return notifications

@router.get("/child/{student_id}/insights")
def get_child_insights(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Security check: ensure this student belongs to the parent
    parent = db.exec(select(Parent).where(Parent.user_id == current_user.id)).first()
    student = db.get(Student, student_id)
    
    if not student or (parent and student.parent_id != parent.id):
        # Allow if admin, but for now strict
        if current_user.role != RoleEnum.admin and student.parent_id != parent.id:
            raise HTTPException(status_code=403, detail="You are not authorized to view this child's insights")

    child_user = db.get(User, student.user_id)
    child_name = child_user.username if child_user else "Ahmad"

    # Try to get real report from DB
    report = db.exec(
        select(StudentReport)
        .where(StudentReport.student_id == student_id)
        .order_by(StudentReport.created_at.desc())
    ).first()

    if report:
        try:
            return json.loads(report.report_data)
        except:
            pass

    # Mock data based on the provided JSON
    insights = {
        "role": "parent",
        "child_name": child_name,
        "time_well_spent": {
            "study_hours_today": "2h 30m",
            "focus_score": "High (82%)",
            "calm_percentage": "88%"
        },
        "daily_snapshot": {
            "overall_mood": "Positive",
            "energy_level": "High",
            "social_engagement": "Great"
        },
        "learning_journey_map": [
            { "stage": "Morning", "activity": "Multiplication Adventure", "success": True },
            { "stage": "Noon", "activity": "Interactive Geometry", "success": True },
            { "stage": "Afternoon", "activity": "Problem Solving Reflection", "success": "N/A" },
            { "stage": "Evening", "activity": "Math Game Recap", "success": False }
        ],
        "sentiment_trend": {
            "values": [65, 70, 85, 80, 90], 
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "description": "Emotional Positivity Index (0-100)"
        },
        "parent_toolkit": {
            "discuss_today": "Your child mastered their 5-times tables today!",
            "suggested_activity": "Try playing the 'Number Jump' game with them before bed to reinforce today's logic.",
            "new_words": ["Product", "Equation", "Factor"]
        }
    }
    return insights

@router.patch("/child/{student_id}/preferences")
def update_child_preferences(
    student_id: int,
    difficulty_level: Optional[int] = None,
    sensory_settings: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    parent = db.exec(select(Parent).where(Parent.user_id == current_user.id)).first()
    student = db.get(Student, student_id)
    
    if not student or (parent and student.parent_id != parent.id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if difficulty_level is not None:
        student.difficulty_level = difficulty_level
    
    if sensory_settings is not None:
        student.sensory_settings = json.dumps(sensory_settings)
    
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return {"message": "Preferences updated successfully"}
