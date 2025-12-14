from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from db.database import engine
from db.crud import create_student, get_all_students, get_student_by_id, update_student, delete_student, get_lessons
from models.student import Student
from models.lesson import Lesson
from schemas.student_schema import StudentCreate, StudentRead, StudentUpdate
from schemas.lesson_schema import LessonRead

# ---------------------------
# Students Router
# ---------------------------
router = APIRouter(prefix="/students", tags=["Students"])

# ---------------------------
# CRUD for Students
# ---------------------------

@router.post("/", response_model=StudentRead)
def create_student_route(student: StudentCreate):
    """
    Create a new student entry in the database.
    """
    student_obj = Student(**student.dict())
    return create_student(student_obj)


@router.get("/", response_model=list[StudentRead])
def get_students_route():
    """
    Retrieve all students from the database.
    """
    return get_all_students()


@router.get("/{student_id}", response_model=StudentRead)
def get_student_route(student_id: int):
    """
    Retrieve a student by their student_id.
    """
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentRead)
def update_student_route(student_id: int, student: StudentUpdate):
    """
    Update an existing student's data.
    """
    updated_student = update_student(student_id, **student.dict(exclude_unset=True))
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student


@router.delete("/{student_id}")
def delete_student_route(student_id: int):
    """
    Delete a student by their student_id.
    """
    deleted_student = delete_student(student_id)
    if not deleted_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"deleted": student_id}


# ---------------------------
# Lessons for a Student (by student_id)
# ---------------------------

@router.get("/{student_id}/lessons", response_model=list[LessonRead])
def get_lessons_route(student_id: int):
    """
    Retrieve all lessons for a given student_id.
    """
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return get_lessons(student_id)
