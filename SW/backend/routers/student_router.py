from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlmodel import Session, select, update
from db.database import engine, get_session
from pathlib import Path
from fastapi.responses import FileResponse
from db.crud import (
    create_student, get_all_students, get_student_by_id, update_student, delete_student,
    get_lessons, get_lessons_grouped_by_milestones, create_lesson, update_lesson,
    get_milestones, get_milestone_by_id, create_milestone, update_milestone, delete_milestone,
    get_quizzes, create_quiz, get_quiz_by_id, update_quiz, delete_quiz,
    get_ask_baseet_conversations, create_ask_baseet, get_ask_baseet_by_id, update_ask_baseet, delete_ask_baseet
)
from models.student import Student
from models.lesson import Lesson
from models.milestone import Milestone
from models.material import Material
from models.assignment import Assignment
from models.quiz import Quiz
from models.ask_baseet import AskBaseet
from schemas.student_schema import StudentCreate, StudentRead, StudentUpdate
from schemas.lesson_schema import LessonRead, LessonUpdate
from schemas.milestone_schema import MilestoneRead, MilestoneCreate, MilestoneUpdate, MilestoneWithLessons
from schemas.material_schema import MaterialRead
from schemas.assignment_schema import AssignmentRead
from schemas.quiz_schema import QuizCreate, QuizRead, QuizUpdate
from schemas.ask_baseet_schema import AskBaseetCreate, AskBaseetRead, AskBaseetUpdate


# ---------------------------
# Students Router
# ---------------------------
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
    updated_student = update_student(
        student_id,
        **student.dict(exclude_unset=True)
    )
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

# @router.get("/{student_id}/dashboard")
# def get_student_dashboard(student_id: int):
#     """
#     Get all student data in one response: lessons (grouped by milestones), materials, assignments, quizzes, and ask-baseet conversations
#     """
#     student = get_student_by_id(student_id)
#     if not student:
#         raise HTTPException(status_code=404, detail="Student not found")
    
#     # Get lessons grouped by milestones
#     grouped_lessons = get_lessons_grouped_by_milestones(student_id)
    
#     # Format lessons data
#     lessons_data = []
#     for item in grouped_lessons:
#         milestone_dict = {
#             "id": item["milestone"].id,
#             "student_id": item["milestone"].student_id,
#             "title": item["milestone"].title,
#             "number": item["milestone"].number,
#             "description": item["milestone"].description,
#             "lessons": [
#                 {
#                     "id": lesson.id,
#                     "student_id": lesson.student_id,
#                     "milestone_number": lesson.milestone_number,
#                     "title": lesson.title,
#                     "lesson_number": lesson.lesson_number,
#                     "progress": lesson.progress,
#                     "status": lesson.status,
#                     "description": lesson.description,
#                 }
#                 for lesson in item["lessons"]
#             ]
#         }

#         lessons_data.append(milestone_dict)
    
#     return {
#         "student_id": student_id,
#         "lessons": lessons_data,  # Now grouped by milestones
#         "materials": get_materials(student_id),
#         "assignments": get_assignments(student_id),
#         "quizzes": get_quizzes(student_id),
#         "ask_baseet": get_ask_baseet_conversations(student_id)
#     }


# ---------------------------
# Milestones endpoints
# ---------------------------

@router.get("/{student_id}/milestones", response_model=list[MilestoneRead])
def get_milestones_route(student_id: int):
    """Retrieve all milestones for a given student_id"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_milestones(student_id)


@router.post("/{student_id}/milestones", response_model=MilestoneRead)
def create_milestone_route(student_id: int, milestone: MilestoneCreate):
    """Create a new milestone for a student"""
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    milestone_data = Milestone(student_id=student_id, **milestone.dict(exclude={"student_id"}))
    return create_milestone(milestone_data)


# ---------------------------
# Lessons for a Student
# ---------------------------

@router.get("/{student_id}/lessons", response_model=list[LessonRead])
def get_lessons_route(student_id: int, session: Session = Depends(get_session)):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    lessons = session.exec(
        select(Lesson).where(Lesson.student_id == student_id)
    ).all()

    # Attach materials to each lesson
    lessons_with_materials = []
    for lesson in lessons:
        materials = session.exec(
            select(Material).where(Material.lesson_id == lesson.id)
        ).all()

        lesson_data = LessonRead(
            id=lesson.id,
            student_id=lesson.student_id,
            milestone_number=lesson.milestone_number,
            lesson_number=lesson.lesson_number,
            title=lesson.title,
            description=lesson.description,
            progress=lesson.progress,
            status=lesson.status,
            number=f"{lesson.milestone_number}.{lesson.lesson_number}",
            materials=materials  # ✅ include materials
        )
        lessons_with_materials.append(lesson_data)

    return lessons_with_materials


@router.get("/{student_id}/lessons/{lesson_id}", response_model=LessonRead)
def get_lesson(student_id: int, lesson_id: int):
    with Session(engine) as session:
        statement = select(Lesson).where(
            Lesson.id == lesson_id,
            Lesson.student_id == student_id
        )
        lesson = session.exec(statement).first()

        if not lesson:
            raise HTTPException(404, detail="Lesson not found")

        return LessonRead(
            id=lesson.id,
            student_id=lesson.student_id,
            milestone_number=lesson.milestone_number,
            lesson_number=lesson.lesson_number,
            title=lesson.title,
            description=lesson.description,
            progress=lesson.progress,
            status=lesson.status,
            number=f"{lesson.milestone_number}.{lesson.lesson_number}"
        )


@router.patch("/{student_id}/lessons/{lesson_id}", response_model=LessonRead)
def reset_lesson_route(student_id: int, lesson_id: int, data: LessonUpdate):
    try:
        with Session(engine) as session:
            # 1️⃣ Get the lesson
            lesson = session.get(Lesson, lesson_id)
            if not lesson or lesson.student_id != student_id:
                raise HTTPException(status_code=404, detail="Lesson not found")

            # 2️⃣ Update progress if provided
            if data.progress is not None:
                lesson.progress = data.progress

            # 3️⃣ Update current lesson status based on progress
            lesson.status = "completed" if lesson.progress == 100 else "in-progress"
            session.add(lesson)
            session.flush()  # ensure SQLModel sees the change

            # 4️⃣ Check if all lessons in this milestone are completed
            milestone_lessons = session.exec(
                select(Lesson).where(
                    Lesson.student_id == student_id,
                    Lesson.milestone_number == lesson.milestone_number
                )
            ).all()

            if all(l.progress == 100 for l in milestone_lessons):
                next_milestone_number = lesson.milestone_number + 1

                # 5️⃣ Unlock next milestone lessons (status = in-progress)
                stmt = (
                    update(Lesson)
                    .where(
                        Lesson.student_id == student_id,
                        Lesson.milestone_number == next_milestone_number,
                        Lesson.status == "locked"
                    )
                    .values(status="in-progress")
                )
                session.exec(stmt)

            session.commit()  # commit everything at once
            session.refresh(lesson)

            return LessonRead(
                id=lesson.id,
                student_id=lesson.student_id,
                milestone_number=lesson.milestone_number,
                lesson_number=lesson.lesson_number,
                title=lesson.title,
                description=lesson.description,
                progress=lesson.progress,
                status=lesson.status,
                number=f"{lesson.milestone_number}.{lesson.lesson_number}"
            )

    except Exception as e:
        print("Error updating lesson:", e)


# ---------------------------
# Materials endpoints
# ---------------------------

UPLOAD_DIR = Path("uploads/materials")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # ensure folder exists

@router.get(
    "/{student_id}/lessons/{lesson_id}/materials",
    response_model=list[MaterialRead]
)
def get_lesson_materials(
    student_id: int,
    lesson_id: int,
    session: Session = Depends(get_session)
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson or lesson.student_id != student_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Return all materials regardless of lesson status
    materials = session.exec(
        select(Material).where(Material.lesson_id == lesson_id)
    ).all()

    return materials


@router.post("/{lesson_id}/materials", response_model=MaterialRead)
async def upload_material(
    lesson_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # clean filename to avoid issues
    safe_filename = f"{lesson_id}_{file.filename.replace(' ', '_')}"
    file_path = UPLOAD_DIR / safe_filename

    # save file to disk
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # save metadata in DB
    material = Material(
        lesson_id=lesson_id,
        title=file.filename,
        description="Uploaded file",
        material_type=file.filename.split(".")[-1],
        file_url=f"/uploads/materials/{safe_filename}"  # URL for frontend
    )
    session.add(material)
    session.commit()
    session.refresh(material)
    return material


@router.get("/students/{student_id}/lessons/{lesson_id}/materials/{material_id}/download")
def download_material(
    student_id: int,
    lesson_id: int,
    material_id: int,
    session: Session = Depends(get_session)
):
    # 1️⃣ Get the material
    material = session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # 2️⃣ Ensure material belongs to the lesson
    if material.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Material does not belong to this lesson")

    # 3️⃣ Build safe file path
    file_path = Path("uploads") / "materials" / Path(material.title).name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # 4️⃣ Return as downloadable file
    return FileResponse(
        path=file_path,
        filename=material.title,
        media_type="application/octet-stream"
    )



# ---------------------------
# Assignments endpoints
# ---------------------------

UPLOAD_DIR = Path("uploads/assignments")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get(
    "/{student_id}/lessons/{lesson_id}/assignments",
    response_model=list[AssignmentRead]
)
def get_lesson_assignments(
    student_id: int,
    lesson_id: int,
    session: Session = Depends(get_session)
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson or lesson.student_id != student_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return session.exec(
        select(Assignment).where(Assignment.lesson_id == lesson_id)
    ).all()


@router.post("/{lesson_id}/assignments", response_model=AssignmentRead)
async def upload_assignment(
    lesson_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    safe_filename = f"{lesson_id}_{file.filename.replace(' ', '_')}"
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    assignment = Assignment(
        lesson_id=lesson_id,
        title=file.filename,
        description="Assignment file",
        assignment_type=file.filename.split(".")[-1],
        file_url=f"/uploads/assignments/{safe_filename}",
    )

    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    return assignment


@router.get(
    "/{student_id}/lessons/{lesson_id}/assignments/{assignment_id}/download"
)
def download_assignment(
    student_id: int,
    lesson_id: int,
    assignment_id: int,
    session: Session = Depends(get_session)
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment or assignment.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Assignment not found")

    file_path = Path("uploads/assignments") / Path(assignment.file_url).name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=assignment.title,
        media_type="application/octet-stream",
    )


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
