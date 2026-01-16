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
from models.content_course import ContentCourse
from models.content_lesson import ContentLesson
from models.content_material import ContentMaterial
from models.content_assignment import ContentAssignment
from models.classroom import Classroom, ClassroomCourseLink
from schemas.student_schema import StudentCreate, StudentRead, StudentUpdate
from schemas.lesson_schema import LessonRead, LessonUpdate
from schemas.milestone_schema import MilestoneRead, MilestoneCreate
from schemas.material_schema import MaterialRead
from schemas.assignment_schema import AssignmentRead
from schemas.course_schema import CourseRead
from schemas.content_schema import ContentCourseRead, ContentLessonRead

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


@router.get("/{student_id}/assigned-courses", response_model=list[ContentCourseRead])
def get_assigned_courses(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if not student.classroom_id:
        return []

    # Get courses assigned to the student's classroom
    statement = (
        select(ContentCourse)
        .join(ClassroomCourseLink, ContentCourse.id == ClassroomCourseLink.course_id)
        .where(ClassroomCourseLink.classroom_id == student.classroom_id)
    )
    courses = session.exec(statement).all()
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
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 1. Start with ContentLessons as the source of truth
    query = select(ContentLesson)
    
    if course_id:
        course = session.get(ContentCourse, course_id)
        if course:
            query = query.where(ContentLesson.course_number == course.course_number)
    
    query = query.order_by(ContentLesson.milestone_number, ContentLesson.lesson_number)
    content_lessons = session.exec(query).all()
    
    # Check if student has ANY lesson records for this course
    # If not, we should unlock the FIRST lesson
    has_progress = False
    if content_lessons:
        p_stmt = select(Lesson).where(Lesson.student_id == student_id)
        # Check for any lesson that links to one of these content_lessons
        cl_ids = [cl.id for cl in content_lessons]
        p_stmt = p_stmt.where(Lesson.content_lesson_id.in_(cl_ids))
        existing_progress = session.exec(p_stmt).first()
        if existing_progress:
            has_progress = True

    lessons_read = []
    
    # Sort content lessons to find the first one
    content_lessons.sort(key=lambda x: (x.milestone_number, x.lesson_number))

    for i, cl in enumerate(content_lessons):
        # 2. Check for student's progress record
        # Find milestone first (legacy structure might still be used for progress)
        # Actually, let's use the new content_lesson_id if possible
        lp_stmt = select(Lesson).where(
            Lesson.student_id == student_id,
            Lesson.content_lesson_id == cl.id
        )
        lesson_progress = session.exec(lp_stmt).first()
        
        # Fallback to old matching if content_lesson_id is not yet set
        if not lesson_progress:
            lp_stmt_old = select(Lesson).where(
                Lesson.student_id == student_id,
                Lesson.lesson_number == cl.lesson_number
            ).join(Milestone).where(Milestone.number == cl.milestone_number)
            
            if course_id:
                lp_stmt_old = lp_stmt_old.where(Milestone.course_id == course_id)
            
            lesson_progress = session.exec(lp_stmt_old).first()
            
            # If found by old way, link it for future
            if lesson_progress:
                lesson_progress.content_lesson_id = cl.id
                session.add(lesson_progress)
                session.commit()

        # 3. Construct LessonRead
        # Default values if no progress record exists
        progress_val = 0
        status_val = "locked" # Default to locked if no record
        lesson_id_val = cl.id # Use Content ID if no instance yet
        
        # AUTO-UNLOCK logic: If it's the first lesson and no progress exists, make it 'in-progress'
        if not has_progress and i == 0:
            status_val = "in-progress"

        if lesson_progress:
            progress_val = lesson_progress.progress
            status_val = lesson_progress.status
            lesson_id_val = lesson_progress.id
        
        # Merge materials (from ContentMaterial)
        # Note: LessonRead.materials expects MaterialRead which has lesson_id.
        # This is student-specific. We might need a ContentMaterialRead instead.
        # For now, I'll adapt it.
        materials = []
        for cm in cl.materials:
            materials.append({
                "id": cm.id,
                "lesson_id": lesson_id_val,
                "title": cm.title,
                "file_url": cm.file_url,
                "material_type": cm.material_type
            })

        lessons_read.append(
            LessonRead(
                id=lesson_id_val,
                student_id=student_id,
                milestone_number=cl.milestone_number,
                lesson_number=cl.lesson_number,
                title=cl.title,
                description=cl.description,
                progress=progress_val,
                status=status_val,
                number=f"{cl.milestone_number}.{cl.lesson_number}",
                course_id=course_id,
                materials=materials
            )
        )
    
    return lessons_read


@router.get("/{student_id}/lessons/{lesson_id}", response_model=LessonRead)
def get_lesson(student_id: int, lesson_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(404, detail="Student not found")

    # 1. Try to find existing lesson record
    lesson = session.get(Lesson, lesson_id)
    
    # Check if this lesson belongs to the student
    if lesson and lesson.student_id != student_id:
        lesson = None

    content_lesson = None
    if lesson and lesson.content_lesson_id:
        content_lesson = session.get(ContentLesson, lesson.content_lesson_id)
    
    # 2. If no lesson record, or we want to support direct access via Content ID
    if not lesson or not content_lesson:
        # Check if lesson_id refers to a ContentLesson instead
        content_lesson = session.get(ContentLesson, lesson_id)
        if content_lesson:
            # Check if student already has a lesson record for this content
            stmt = select(Lesson).where(
                Lesson.student_id == student_id,
                Lesson.content_lesson_id == content_lesson.id
            )
            lesson = session.exec(stmt).first()
            
            if not lesson:
                # Instantiate it!
                # We need to find the milestone for the student that matches this content lesson
                # This part is a bit tricky if milestones aren't already set up for student.
                # I'll try to find or create a milestone if needed, or just set it to None for now.
                # Actually, I'll look for a milestone with the same number and course_id.
                course_stmt = select(ContentCourse).where(ContentCourse.course_number == content_lesson.course_number)
                course = session.exec(course_stmt).first()
                
                milestone_id = None
                if course:
                    m_stmt = select(Milestone).where(
                        Milestone.course_id == course.id,
                        Milestone.number == content_lesson.milestone_number
                    )
                    milestone_obj = session.exec(m_stmt).first()
                    if milestone_obj:
                        milestone_id = milestone_obj.id

                lesson = Lesson(
                    student_id=student_id,
                    content_lesson_id=content_lesson.id,
                    milestone_id=milestone_id,
                    lesson_number=content_lesson.lesson_number,
                    title=content_lesson.title, # Snapshot for convenience
                    description=content_lesson.description,
                    status="in-progress", # First access unlocks it
                    progress=0
                )
                session.add(lesson)
                session.commit()
                session.refresh(lesson)

    if not lesson or not content_lesson:
        raise HTTPException(404, detail="Lesson not found")

    # 3. Merge and Return
    # Materials (from content)
    materials = [
        {
            "id": cm.id,
            "lesson_id": lesson.id,
            "title": cm.title,
            "file_url": cm.file_url,
            "material_type": cm.material_type
        }
        for cm in content_lesson.materials
    ]

    return LessonRead(
        id=lesson.id,
        student_id=lesson.student_id,
        milestone_number=content_lesson.milestone_number,
        lesson_number=content_lesson.lesson_number,
        title=content_lesson.title,
        description=content_lesson.description,
        progress=lesson.progress,
        status=lesson.status,
        number=f"{content_lesson.milestone_number}.{content_lesson.lesson_number}",
        course_id=None, # We can fetch if needed
        materials=materials
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
    # 1. Try finding Lesson instance
    lesson = session.get(Lesson, lesson_id)
    
    # 2. If no instance, lesson_id might be a ContentLesson.id
    content_lesson = None
    if lesson and lesson.student_id == student_id:
        if lesson.content_lesson_id:
            content_lesson = session.get(ContentLesson, lesson.content_lesson_id)
    else:
        # Check if it's a template ID
        content_lesson = session.get(ContentLesson, lesson_id)

    if not content_lesson and not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # If we have a template, return its materials
    if content_lesson:
        return [
            MaterialRead(
                id=cm.id,
                lesson_id=lesson_id, # return the ID we were asked for
                title=cm.title,
                file_url=cm.file_url,
                material_type=cm.material_type,
                description=None
            )
            for cm in content_lesson.materials
        ]

    # Legacy: search by lesson_id in materials table
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
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    lesson = session.get(Lesson, lesson_id)
    content_lesson = None
    
    # If instance found
    if lesson and lesson.student_id == student_id:
        if lesson.content_lesson_id:
            content_lesson = session.get(ContentLesson, lesson.content_lesson_id)
    else:
        # Check if lesson_id refers to Content ID instead
        content_lesson = session.get(ContentLesson, lesson_id)

    if not content_lesson and not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Determine ContentLesson ID
    content_lesson_id = None
    if content_lesson:
        content_lesson_id = content_lesson.id
    elif lesson:
        content_lesson_id = lesson.content_lesson_id
        if not content_lesson_id:
            # Try to find it by numbers (fallback)
            milestone = lesson.milestone
            if milestone:
                course = session.get(ContentCourse, milestone.course_id)
                if course:
                    cl_stmt = select(ContentLesson).where(
                        ContentLesson.course_number == course.course_number,
                        ContentLesson.milestone_number == milestone.number,
                        ContentLesson.lesson_number == lesson.lesson_number
                    )
                    cl = session.exec(cl_stmt).first()
                    if cl:
                        content_lesson_id = cl.id
                        lesson.content_lesson_id = cl.id
                        session.add(lesson)
                        session.commit()

    # Fetch ContentAssignments (Templates)
    if content_lesson_id:
        ca_stmt = select(ContentAssignment).where(ContentAssignment.lesson_id == content_lesson_id)
        content_assignments = session.exec(ca_stmt).all()
    else:
        content_assignments = []

    result = []
    for ca in content_assignments:
        # Match with student instance
        sa_stmt = select(Assignment).where(
            Assignment.lesson_id == lesson_id,
            Assignment.content_assignment_id == ca.id
        )
        # Handle student_id check in sa_stmt if lesson exists
        if lesson:
            sa_stmt = sa_stmt.where(Assignment.student_id == student_id)
            
        student_assign = session.exec(sa_stmt).first()
        
        # Merge data
        assign_id = student_assign.id if student_assign else ca.id # Use CA ID as fallback
        title = ca.title
        description = ca.description
        assignment_type = ca.assignment_type
        file_url = ca.file_url
        deadline = student_assign.deadline if student_assign else None
        
        result.append({
            "id": assign_id,
            "content_assignment_id": ca.id,
            "lesson_id": lesson_id,
            "title": title,
            "description": description,
            "assignment_type": assignment_type or "unknown",
            "file_url": file_url or "",
            "deadline": deadline.isoformat() if deadline else None
        })

    # Also include legacy assignments if any (for backward compatibility during migration)
    if lesson:
        legacy_stmt = select(Assignment).where(
            Assignment.lesson_id == lesson_id,
            Assignment.content_assignment_id == None
        )
        legacy_assigns = session.exec(legacy_stmt).all()
        for la in legacy_assigns:
            result.append({
                "id": la.id,
                "content_assignment_id": None,
                "lesson_id": la.lesson_id,
                "title": la.title,
                "description": la.description,
                "assignment_type": la.assignment_type or "unknown",
                "file_url": la.file_url or "",
                "deadline": la.deadline.isoformat() if la.deadline else None
            })

    return result


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
