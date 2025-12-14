from fastapi import APIRouter, HTTPException
from typing import List
from db.crud import (
    create_student, get_all_students, get_student_by_id, update_student, delete_student,
    get_lessons, create_lesson, get_lesson_by_id, update_lesson,
    get_materials, create_material, get_material_by_id, update_material, delete_material,
    get_assignments, create_assignment, get_assignment_by_id, update_assignment, delete_assignment,
    get_quizzes, create_quiz, get_quiz_by_id, update_quiz, delete_quiz,
    get_ask_baseet_conversations, create_ask_baseet, get_ask_baseet_by_id, update_ask_baseet, delete_ask_baseet
)
from models.student import Student
from models.lesson import Lesson
from models.material import Material
from models.assignment import Assignment
from models.quiz import Quiz
from models.ask_baseet import AskBaseet
from schemas.student_schema import StudentCreate, StudentRead, StudentUpdate
from schemas.lesson_schema import LessonRead, LessonCreate
from schemas.material_schema import MaterialCreate, MaterialRead, MaterialUpdate
from schemas.assignment_schema import AssignmentCreate, AssignmentRead, AssignmentUpdate
from schemas.quiz_schema import QuizCreate, QuizRead, QuizUpdate
from schemas.ask_baseet_schema import AskBaseetCreate, AskBaseetRead, AskBaseetUpdate

router = APIRouter(prefix="/students", tags=["Students"])

# ---------------------------
# Student CRUD
# ---------------------------

@router.post("/", response_model=StudentRead)
def create_student_route(student: StudentCreate):
    student_obj = Student(**student.dict())
    return create_student(student_obj)


@router.get("/", response_model=list[StudentRead])
def get_students_route():
    return get_all_students()


@router.get("/{student_id}", response_model=StudentRead)
def get_student_route(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentRead)
def update_student_route(student_id: int, student: StudentUpdate):
    updated_student = update_student(student_id, **student.dict(exclude_unset=True))
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student


@router.delete("/{student_id}")
def delete_student_route(student_id: int):
    deleted_student = delete_student(student_id)
    if not deleted_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"deleted": student_id}


# ---------------------------
# Dashboard - Aggregated endpoint
# ---------------------------

@router.get("/{student_id}/dashboard")
def get_student_dashboard(student_id: int):
    """
    Get all student data in one response: lessons, materials, assignments, quizzes, and ask-baseet conversations
    """
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "student_id": student_id,
        "lessons": get_lessons(student_id),
        "materials": get_materials(student_id),
        "assignments": get_assignments(student_id),
        "quizzes": get_quizzes(student_id),
        "ask_baseet": get_ask_baseet_conversations(student_id)
    }


# ---------------------------
# Lessons endpoints
# ---------------------------

@router.get("/{student_id}/lessons", response_model=list[LessonRead])
def get_lessons_route(student_id: int):
    """Retrieve all lessons for a given student_id"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_lessons(student_id)


@router.post("/{student_id}/lessons", response_model=LessonRead)
def create_lesson_route(student_id: int, lesson: LessonCreate):
    """Create a new lesson for a student"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    lesson_data = Lesson(student_id=student_id, **lesson.dict())
    return create_lesson(lesson_data)


# ---------------------------
# Materials endpoints
# ---------------------------

@router.get("/{student_id}/materials", response_model=list[MaterialRead])
def get_materials_route(student_id: int):
    """Retrieve all materials for a given student_id"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_materials(student_id)


@router.post("/{student_id}/materials", response_model=MaterialRead)
def create_material_route(student_id: int, material: MaterialCreate):
    """Create a new material for a student"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    material_data = Material(student_id=student_id, **material.dict(exclude={"student_id"}))
    return create_material(material_data)


@router.get("/{student_id}/materials/{material_id}", response_model=MaterialRead)
def get_material_route(student_id: int, material_id: int):
    """Get a specific material"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    material = get_material_by_id(material_id)
    if not material or material.student_id != student_id:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.put("/{student_id}/materials/{material_id}", response_model=MaterialRead)
def update_material_route(student_id: int, material_id: int, material: MaterialUpdate):
    """Update a material"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_material = get_material_by_id(material_id)
    if not existing_material or existing_material.student_id != student_id:
        raise HTTPException(status_code=404, detail="Material not found")
    
    updated = update_material(material_id, **material.dict(exclude_unset=True))
    return updated


@router.delete("/{student_id}/materials/{material_id}")
def delete_material_route(student_id: int, material_id: int):
    """Delete a material"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    material = get_material_by_id(material_id)
    if not material or material.student_id != student_id:
        raise HTTPException(status_code=404, detail="Material not found")
    
    delete_material(material_id)
    return {"deleted": material_id}


# ---------------------------
# Assignments endpoints
# ---------------------------

@router.get("/{student_id}/assignments", response_model=list[AssignmentRead])
def get_assignments_route(student_id: int):
    """Retrieve all assignments for a given student_id"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_assignments(student_id)


@router.post("/{student_id}/assignments", response_model=AssignmentRead)
def create_assignment_route(student_id: int, assignment: AssignmentCreate):
    """Create a new assignment for a student"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    assignment_data = Assignment(student_id=student_id, **assignment.dict(exclude={"student_id"}))
    return create_assignment(assignment_data)


@router.get("/{student_id}/assignments/{assignment_id}", response_model=AssignmentRead)
def get_assignment_route(student_id: int, assignment_id: int):
    """Get a specific assignment"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    assignment = get_assignment_by_id(assignment_id)
    if not assignment or assignment.student_id != student_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.put("/{student_id}/assignments/{assignment_id}", response_model=AssignmentRead)
def update_assignment_route(student_id: int, assignment_id: int, assignment: AssignmentUpdate):
    """Update an assignment (e.g., submit assignment)"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_assignment = get_assignment_by_id(assignment_id)
    if not existing_assignment or existing_assignment.student_id != student_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    updated = update_assignment(assignment_id, **assignment.dict(exclude_unset=True))
    return updated


@router.delete("/{student_id}/assignments/{assignment_id}")
def delete_assignment_route(student_id: int, assignment_id: int):
    """Delete an assignment"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    assignment = get_assignment_by_id(assignment_id)
    if not assignment or assignment.student_id != student_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    delete_assignment(assignment_id)
    return {"deleted": assignment_id}


# ---------------------------
# Quizzes endpoints
# ---------------------------

@router.get("/{student_id}/quizzes", response_model=list[QuizRead])
def get_quizzes_route(student_id: int):
    """Retrieve all quizzes for a given student_id"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_quizzes(student_id)


@router.post("/{student_id}/quizzes", response_model=QuizRead)
def create_quiz_route(student_id: int, quiz: QuizCreate):
    """Create a new quiz for a student"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    quiz_data = Quiz(student_id=student_id, **quiz.dict(exclude={"student_id"}))
    return create_quiz(quiz_data)


@router.get("/{student_id}/quizzes/{quiz_id}", response_model=QuizRead)
def get_quiz_route(student_id: int, quiz_id: int):
    """Get a specific quiz"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    quiz = get_quiz_by_id(quiz_id)
    if not quiz or quiz.student_id != student_id:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.put("/{student_id}/quizzes/{quiz_id}", response_model=QuizRead)
def update_quiz_route(student_id: int, quiz_id: int, quiz: QuizUpdate):
    """Update a quiz (e.g., submit answers, update status)"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_quiz = get_quiz_by_id(quiz_id)
    if not existing_quiz or existing_quiz.student_id != student_id:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    updated = update_quiz(quiz_id, **quiz.dict(exclude_unset=True))
    return updated


@router.delete("/{student_id}/quizzes/{quiz_id}")
def delete_quiz_route(student_id: int, quiz_id: int):
    """Delete a quiz"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    quiz = get_quiz_by_id(quiz_id)
    if not quiz or quiz.student_id != student_id:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    delete_quiz(quiz_id)
    return {"deleted": quiz_id}


# ---------------------------
# Ask Baseet endpoints
# ---------------------------

@router.get("/{student_id}/ask-baseet", response_model=list[AskBaseetRead])
def get_ask_baseet_route(student_id: int):
    """Retrieve all Ask Baseet conversations for a given student_id"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_ask_baseet_conversations(student_id)


@router.post("/{student_id}/ask-baseet", response_model=AskBaseetRead)
def create_ask_baseet_route(student_id: int, ask_baseet: AskBaseetCreate):
    """Create a new Ask Baseet question"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    ask_baseet_data = AskBaseet(student_id=student_id, **ask_baseet.dict(exclude={"student_id"}))
    return create_ask_baseet(ask_baseet_data)


@router.get("/{student_id}/ask-baseet/{ask_baseet_id}", response_model=AskBaseetRead)
def get_ask_baseet_by_id_route(student_id: int, ask_baseet_id: int):
    """Get a specific Ask Baseet conversation"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    ask_baseet = get_ask_baseet_by_id(ask_baseet_id)
    if not ask_baseet or ask_baseet.student_id != student_id:
        raise HTTPException(status_code=404, detail="Ask Baseet conversation not found")
    return ask_baseet


@router.put("/{student_id}/ask-baseet/{ask_baseet_id}", response_model=AskBaseetRead)
def update_ask_baseet_route(student_id: int, ask_baseet_id: int, ask_baseet: AskBaseetUpdate):
    """Update an Ask Baseet conversation (e.g., add answer)"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_ask_baseet = get_ask_baseet_by_id(ask_baseet_id)
    if not existing_ask_baseet or existing_ask_baseet.student_id != student_id:
        raise HTTPException(status_code=404, detail="Ask Baseet conversation not found")
    
    updated = update_ask_baseet(ask_baseet_id, **ask_baseet.dict(exclude_unset=True))
    return updated


@router.delete("/{student_id}/ask-baseet/{ask_baseet_id}")
def delete_ask_baseet_route(student_id: int, ask_baseet_id: int):
    """Delete an Ask Baseet conversation"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    ask_baseet = get_ask_baseet_by_id(ask_baseet_id)
    if not ask_baseet or ask_baseet.student_id != student_id:
        raise HTTPException(status_code=404, detail="Ask Baseet conversation not found")
    
    delete_ask_baseet(ask_baseet_id)
    return {"deleted": ask_baseet_id}
