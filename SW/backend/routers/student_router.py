# routers/students.py
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlmodel import Session, select, update
from pathlib import Path
from fastapi.responses import FileResponse
from services.ocr import process_image_for_ocr, process_pdf_for_ocr
from datetime import datetime
from db.database import engine, get_session
from db.crud import (
    create_student, get_all_students, get_student_by_id, update_student, delete_student,
    get_milestones, create_milestone, get_courses
)
from models.student import Student
from models.lesson import Lesson
from models.milestone import Milestone
from models.material import Material
from models.assignment import Assignment
from models.submission import Submission
from models.submission_file import SubmissionFile
from models.feedback import Feedback
from models.course import Course
from schemas.student_schema import StudentCreate, StudentRead, StudentUpdate
from schemas.lesson_schema import LessonRead, LessonUpdate
from schemas.milestone_schema import MilestoneRead, MilestoneCreate
from schemas.material_schema import MaterialRead
from schemas.assignment_schema import AssignmentRead
from schemas.course_schema import CourseRead

import traceback

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

@router.get("/courses", response_model=list[CourseRead])
def get_courses_route():
    courses = get_courses()
    return courses

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
# Milestones endpoints
# ---------------------------
@router.get("/{student_id}/milestones", response_model=list[MilestoneRead])
def get_milestones_route(student_id: int, course_id: int = None):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return get_milestones(student_id, course_id)


@router.post("/{student_id}/milestones", response_model=MilestoneRead)
def create_milestone_route(student_id: int, milestone: MilestoneCreate):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    milestone_data = Milestone(student_id=student_id, **milestone.dict(exclude={"student_id"}))
    return create_milestone(milestone_data)


# ---------------------------
# Lessons endpoints
# ---------------------------
@router.get("/{student_id}/lessons", response_model=list[LessonRead])
def get_lessons_route(student_id: int, course_id: int = None, session: Session = Depends(get_session)):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    query = select(Lesson).where(Lesson.student_id == student_id)
    
    # Join with Milestone for ordering and filtering
    query = query.join(Milestone)
    
    if course_id:
        query = query.where(Milestone.course_id == course_id)

    query = query.order_by(Milestone.number, Lesson.lesson_number)

    lessons = session.exec(query).all()
    lessons_with_materials = []

    for lesson in lessons:
        materials = session.exec(select(Material).where(Material.lesson_id == lesson.id)).all()
        lessons_with_materials.append(
            LessonRead(
                id=lesson.id,
                student_id=lesson.student_id,
                milestone_number=lesson.milestone_number,
                lesson_number=lesson.lesson_number,
                title=lesson.title,
                description=lesson.description,
                progress=lesson.progress,
                status=lesson.status,
                number=f"{lesson.milestone_number}.{lesson.lesson_number}",
                course_id=lesson.course_id,
                materials=materials
            )
        )

    return lessons_with_materials


@router.get("/{student_id}/lessons/{lesson_id}", response_model=LessonRead)
def get_lesson(student_id: int, lesson_id: int):
    with Session(engine) as session:
        lesson = session.get(Lesson, lesson_id)
        if not lesson or lesson.student_id != student_id:
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
def update_lesson_route(student_id: int, lesson_id: int, data: LessonUpdate):
    with Session(engine) as session:
        lesson = session.get(Lesson, lesson_id)
        if not lesson or lesson.student_id != student_id:
            raise HTTPException(status_code=404, detail="Lesson not found")

        if data.progress is not None:
            lesson.progress = data.progress
        lesson.status = "completed" if lesson.progress == 100 else "in-progress"
        session.add(lesson)
        session.flush()

        milestone_lessons = session.exec(
            select(Lesson).where(
                Lesson.student_id == student_id,
                Lesson.milestone_number == lesson.milestone_number
            )
        ).all()

        if all(l.progress == 100 for l in milestone_lessons):
            next_milestone_number = lesson.milestone_number + 1
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

        session.commit()
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


# ---------------------------
# Materials endpoints
# ---------------------------
MATERIAL_UPLOAD_DIR = Path("uploads/materials")
MATERIAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/{student_id}/lessons/{lesson_id}/materials", response_model=list[MaterialRead])
def get_lesson_materials(student_id: int, lesson_id: int, session: Session = Depends(get_session)):
    lesson = session.get(Lesson, lesson_id)
    if not lesson or lesson.student_id != student_id:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return session.exec(select(Material).where(Material.lesson_id == lesson_id)).all()


@router.post("/{lesson_id}/materials", response_model=MaterialRead)
async def upload_material(
    lesson_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Save file
    safe_filename = f"{lesson_id}_{file.filename.replace(' ', '_')}"
    file_path = MATERIAL_UPLOAD_DIR / safe_filename

    file_bytes = await file.read()

    with open(file_path, "wb") as f:
        f.write(file_bytes)


    # -------- OCR PART --------
    extracted_text = None
    file_ext = file.filename.lower()

    try:
        if file_ext.endswith(".pdf"):
            extracted_text = process_pdf_for_ocr(file_bytes, "ara+eng")
        elif file_ext.endswith((".png", ".jpg", ".jpeg")):
            extracted_text = process_image_for_ocr(file_bytes, "ara+eng")
    except Exception as e:
        print("OCR failed:", e)
        traceback.print_exc()
        extracted_text = None
    # --------------------------

    material = Material(
        lesson_id=lesson_id,
        title=file.filename,
        description="Uploaded file",
        material_type=file.filename.split(".")[-1],
        file_url=f"/uploads/materials/{safe_filename}",
        extracted_text=extracted_text
    )

    session.add(material)
    session.commit()
    session.refresh(material)
    return material


@router.get("/students/{student_id}/lessons/{lesson_id}/materials/{material_id}/download")
def download_material(student_id: int, lesson_id: int, material_id: int, session: Session = Depends(get_session)):
    material = session.get(Material, material_id)
    if not material or material.lesson_id != lesson_id:
        raise HTTPException(status_code=404, detail="Material not found")

    file_path = Path("uploads/materials") / Path(material.file_url).name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=material.title, media_type="application/octet-stream")



# ---------------------------
# Assignments endpoints
# ---------------------------
ASSIGNMENT_UPLOAD_DIR = Path("uploads/assignments")
ASSIGNMENT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/{student_id}/lessons/{lesson_id}/assignments")
def get_lesson_assignments(
    student_id: int,
    lesson_id: int,
    session: Session = Depends(get_session)
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson or lesson.student_id != student_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    assignments = session.exec(
        select(Assignment).where(Assignment.lesson_id == lesson_id)
    ).all()

    return [
        {
            "id": a.id,
            "lesson_id": a.lesson_id,
            "title": a.title,
            "description": a.description,
            "assignment_type": a.assignment_type or "unknown",
            "file_url": a.file_url or "",
            "deadline": a.deadline.isoformat() if a.deadline else None
        }
        for a in assignments
    ]


@router.post("/{lesson_id}/assignments")
async def upload_assignment(
    lesson_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    lesson = session.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    safe_filename = f"{lesson_id}_{file.filename.replace(' ', '_')}"
    file_path = ASSIGNMENT_UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    assignment = Assignment(
        lesson_id=lesson_id,
        title=file.filename,
        description="Assignment file",
        assignment_type=file.filename.split(".")[-1],
        file_url=f"/uploads/assignments/{safe_filename}",
        deadline=None
    )

    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    return assignment


@router.get("/{student_id}/assignments/{assignment_id}/submission")
def get_submission(
    student_id: int,
    assignment_id: int,
    session: Session = Depends(get_session)
):
    submission = session.exec(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        )
        .order_by(Submission.submitted_at.desc())
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    feedback = session.exec(
        select(Feedback).where(Feedback.submission_id == submission.id)
    ).first()

    files = session.exec(
        select(SubmissionFile).where(SubmissionFile.submission_id == submission.id)
    ).all()

    return {
        "id": submission.id,
        "submitted_at": submission.submitted_at,
        "updated_at": submission.updated_at,
        "description": submission.description,
        "submission_files": [
            {"file_name": f.file_name, "file_url": f.file_url}
            for f in files
        ],
        "feedback": (
            {
                "comment": feedback.comment,
                "rating": feedback.rating
            }
            if feedback else None
        )
    }


@router.post("/{student_id}/assignments/{assignment_id}/submit")
async def submit_assignment(
    student_id: int,
    assignment_id: int,
    description: str = Form(None),
    files: list[UploadFile] = File(...),
    session: Session = Depends(get_session)
):
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    lesson = session.get(Lesson, assignment.lesson_id)
    if lesson.status == "locked":
        raise HTTPException(status_code=403, detail="Lesson is locked")

    submission = Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        description=description
    )

    session.add(submission)
    session.commit()
    session.refresh(submission)

    for file in files:
        safe_name = f"{submission.id}_{file.filename.replace(' ', '_')}"
        file_path = ASSIGNMENT_UPLOAD_DIR / safe_name

        with open(file_path, "wb") as f:
            f.write(await file.read())

        session.add(
            SubmissionFile(
                submission_id=submission.id,
                file_name=file.filename,
                file_url=f"/uploads/assignments/{safe_name}"
            )
        )

    session.commit()

    feedback = session.exec(
        select(Feedback).where(Feedback.submission_id == submission.id)
    ).first()

    submission_files = session.exec(
        select(SubmissionFile).where(SubmissionFile.submission_id == submission.id)
    ).all()

    return {
        "id": submission.id,
        "submitted_at": submission.submitted_at,
        "updated_at": submission.updated_at,
        "description": submission.description,
        "submission_files": [
            {"file_name": f.file_name, "file_url": f.file_url}
            for f in submission_files
        ],
        "feedback": (
            {
                "comment": feedback.comment,
                "rating": feedback.rating
            }
            if feedback else None
        )
    }
