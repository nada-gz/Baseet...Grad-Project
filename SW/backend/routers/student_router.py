# routers/students.py
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from sqlmodel import Session, select, update
from pathlib import Path
from fastapi.responses import FileResponse
from services.ocr import process_image_for_ocr, process_pdf_for_ocr
from models.parent_extensions import LinkingCode
from datetime import datetime, timedelta
import random
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
from models.content_assignment_file import ContentAssignmentFile
from models.classroom import Classroom, ClassroomCourseLink
from schemas.student_schema import StudentCreate, StudentRead, StudentUpdate, StudentProfileDetail
from models.class_level import ClassLevel
from schemas.lesson_schema import LessonRead, LessonUpdate
from schemas.milestone_schema import MilestoneRead, MilestoneCreate
from schemas.material_schema import MaterialRead
from schemas.assignment_schema import AssignmentRead
from schemas.course_schema import CourseRead
from schemas.content_schema import ContentCourseRead, ContentLessonRead
from models.user import User, RoleEnum
from utils.auth import get_current_user

import traceback

# ---------------------------
# Students Router
# ---------------------------

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/linking-code")
def generate_linking_code(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if current_user.role != RoleEnum.student:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    student = session.exec(select(Student).where(Student.user_id == current_user.id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")
    
    # Generate 6-digit code
    code = "".join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Create or update existing code for this student
    existing = session.exec(select(LinkingCode).where(LinkingCode.student_id == student.id, LinkingCode.is_used == False)).first()
    if existing:
        existing.code = code
        existing.expires_at = datetime.utcnow() + timedelta(minutes=15)
        session.add(existing)
        db_obj = existing
    else:
        db_obj = LinkingCode(
            student_id=student.id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        session.add(db_obj)
    
    session.commit()
    session.refresh(db_obj)
    
    return {"code": code, "expires_at": db_obj.expires_at}

SUBMISSION_UPLOAD_DIR = Path("uploads/submissions")
SUBMISSION_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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

@router.get("/{student_id}/profile", response_model=StudentProfileDetail)
def get_student_profile(student_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Student, User, Classroom, ClassLevel)
        .join(User, Student.user_id == User.id)
        .outerjoin(Classroom, Student.classroom_id == Classroom.id)
        .outerjoin(ClassLevel, Classroom.level_id == ClassLevel.id)
        .where(Student.id == student_id)
    )
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
        
    student_obj, user_obj, classroom_obj, level_obj = result
    
    return StudentProfileDetail(
        id=student_obj.id,
        user_id=student_obj.user_id,
        username=user_obj.username,
        email=user_obj.email,
        role=user_obj.role.value,
        age=student_obj.age,
        autism_type=student_obj.autism_type,
        sensitivities=student_obj.sensitivities,
        learning_style=student_obj.learning_style,
        baseline_engagement=student_obj.baseline_engagement,
        classroom_name=classroom_obj.name if classroom_obj else None,
        level_name=level_obj.name if level_obj else None,
        is_flagged=student_obj.is_flagged,
        online=(student_obj.id % 2 == 0) # Simulation for demo
    )


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

    prev_status = "completed" # Theoretical status of the "0-th" lesson to unlock the 1st
    for i, cl in enumerate(content_lessons):
        # 2. Check for student's progress record
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
            
            if lesson_progress:
                lesson_progress.content_lesson_id = cl.id
                session.add(lesson_progress)
                session.commit()

        # 3. Construct LessonRead
        progress_val = 0
        status_val = "locked" 
        lesson_id_val = cl.id 
        
        if lesson_progress:
            progress_val = lesson_progress.progress
            status_val = lesson_progress.status
            lesson_id_val = lesson_progress.id
        else:
            # AUTO-UNLOCK logic: If previous lesson was completed, this one is in-progress
            if prev_status == "completed":
                status_val = "in-progress"

        # Update prev_status for the next iteration
        prev_status = status_val

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

        # Find the milestone number for this lesson
        milestone = session.get(Milestone, lesson.milestone_id)
        if not milestone:
            # Try finding via ContentLesson if milestone_id is missing
            cl = session.get(ContentLesson, lesson.content_lesson_id)
            milestone_num = cl.milestone_number if cl else 0
        else:
            milestone_num = milestone.number

        # 1. Get all ContentLessons for this milestone to know what SHOULD be completed
        course_number = None
        if lesson.content_lesson_id:
            cl = session.get(ContentLesson, lesson.content_lesson_id)
            course_number = cl.course_number
        
        cl_stmt = select(ContentLesson).where(ContentLesson.milestone_number == milestone_num)
        if course_number:
            cl_stmt = cl_stmt.where(ContentLesson.course_number == course_number)
        
        required_content_lessons = session.exec(cl_stmt).all()
        required_ids = [rcl.id for rcl in required_content_lessons]

        # 2. Check student's progress for these specific content lessons
        completed_stmt = select(Lesson).where(
            Lesson.student_id == student_id,
            Lesson.content_lesson_id.in_(required_ids),
            Lesson.status == "completed"
        )
        completed_lessons = session.exec(completed_stmt).all()

        # 3. If all content lessons for this milestone have a 'completed' record, unlock the next milestone
        if len(completed_lessons) >= len(required_ids):
            next_milestone_number = milestone_num + 1
            
            # Find all ContentLessons in the NEXT milestone to unlock their first one (or all)
            # Actually, standard logic is usually to unlock the first lesson or the whole milestone
            # Here we follow the existing pattern of updating matching Lesson records if they exist
            # But they might NOT exist yet.
            
            # Update existing locked records
            # We must join Milestone to find by number safely
            # Or use ContentLesson join which is safer
            locked_stmt = select(Lesson).join(ContentLesson, Lesson.content_lesson_id == ContentLesson.id).where(
                Lesson.student_id == student_id,
                ContentLesson.milestone_number == next_milestone_number,
                Lesson.status == "locked"
            )
            locked_lessons = session.exec(locked_stmt).all()
            for ll in locked_lessons:
                ll.status = "in-progress"
                session.add(ll)

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
        if content_lesson:
            # We found a content lesson, but we have no student progress record (Lesson)
            # We must create it to avoid ForeignKeyViolation in Assignment creation
            
            # 1. Ensure Milestone exists
            m_stmt = select(Milestone).where(
                Milestone.student_id == student_id,
                Milestone.number == content_lesson.milestone_number
            )
            # For simplicity, we just find by number and student_id
            ms = session.exec(m_stmt).first()
            if not ms:
                ms = Milestone(
                    student_id=student_id,
                    number=content_lesson.milestone_number,
                    title=f"Milestone {content_lesson.milestone_number}"
                )
                session.add(ms)
                session.commit()
                session.refresh(ms)
            
            # 2. Create Lesson record
            lesson = Lesson(
                student_id=student_id,
                content_lesson_id=content_lesson.id,
                milestone_id=ms.id,
                lesson_number=content_lesson.lesson_number,
                title=content_lesson.title,
                description=content_lesson.description,
                status="in-progress"
            )
            session.add(lesson)
            session.commit()
            session.refresh(lesson)
            
            # CRITICAL: Update lesson_id to the newly created student-specific ID
            lesson_id = lesson.id

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
                from models.content_course import ContentCourse
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
            
        student_assign = session.exec(sa_stmt).first()
        
        # Auto-create if missing (Eager initialization)
        if not student_assign:
            # We need to create a new Assignment record for this student/lesson/content
            student_assign = Assignment(
                lesson_id=lesson_id, # This is the student's Lesson instance ID
                content_assignment_id=ca.id,
                title=ca.title,
                description=ca.description,
                assignment_type=ca.assignment_type,
                file_url=ca.file_url,
                deadline=None # or derive from somewhere
            )
            session.add(student_assign)
            session.commit()
            session.refresh(student_assign)
        
        # Merge data
        assign_id = student_assign.id
        title = student_assign.title
        description = student_assign.description
        assignment_type = student_assign.assignment_type
        file_url = student_assign.file_url
        deadline = student_assign.deadline
        
        # Prepare files list
        files_list = []
        if ca.files:
            files_list = [
                {"id": f.id, "file_name": f.file_name, "file_url": f.file_url}
                for f in ca.files
            ]

        # Fetch submission
        sub_stmt = select(Submission).where(
            Submission.assignment_id == student_assign.id,
            Submission.student_id == student_id
        ).options(selectinload(Submission.files), selectinload(Submission.feedback))
        submission = session.exec(sub_stmt).first()
        
        submission_data = None
        if submission:
            status = "submitted"
            timing = submission.submitted_at
            if submission.updated_at:
                status = "resubmitted"
                timing = submission.updated_at
            if submission.feedback:
                status = "evaluated"
                # timing remains submission/resubmission date as per user request

            submission_data = {
                "id": submission.id,
                "status": status,
                "description": submission.description,
                "timing": timing.isoformat() if timing else None,
                "updated_at": submission.updated_at.isoformat() if submission.updated_at else None,
                "feedback": {
                    "comment": submission.feedback.comment,
                    "rating": submission.feedback.rating
                } if submission.feedback else None,
                "files": [
                    {"file_name": f.file_name, "file_url": f.file_url}
                    for f in submission.files
                ]
            }

        result.append({
            "id": assign_id,
            "content_assignment_id": ca.id,
            "lesson_id": lesson_id,
            "title": title,
            "description": description,
            "assignment_type": assignment_type or "unknown",
            "file_url": file_url or "",
            "files": files_list,
            "deadline": ca.deadline.isoformat() if (ca.deadline) else (deadline.isoformat() if deadline else None),
            "submission": submission_data
        })

    # Also include legacy assignments if any (for backward compatibility during migration)
    if lesson:
        legacy_stmt = select(Assignment).where(
            Assignment.lesson_id == lesson_id,
            Assignment.content_assignment_id == None
        )
        legacy_assigns = session.exec(legacy_stmt).all()
        for la in legacy_assigns:
            # Fetch submission for legacy
            sub_stmt = select(Submission).where(
                Submission.assignment_id == la.id,
                Submission.student_id == student_id
            ).options(selectinload(Submission.files), selectinload(Submission.feedback))
            submission = session.exec(sub_stmt).first()
            
            submission_data = None
            if submission:
                status = "submitted"
                timing = submission.submitted_at
                if submission.updated_at:
                    status = "resubmitted"
                    timing = submission.updated_at
                if submission.feedback:
                    status = "evaluated"
                    # timing remains submission/resubmission date

                submission_data = {
                    "id": submission.id,
                    "status": status,
                    "description": submission.description,
                    "timing": timing.isoformat() if timing else None,
                    "feedback": {
                        "comment": submission.feedback.comment,
                        "rating": submission.feedback.rating
                    } if submission.feedback else None,
                    "files": [
                        {"file_name": f.file_name, "file_url": f.file_url}
                        for f in submission.files
                    ]
                }

            result.append({
                "id": la.id,
                "content_assignment_id": None,
                "lesson_id": la.lesson_id,
                "title": la.title,
                "description": la.description,
                "assignment_type": "legacy",
                "file_url": "",
                "files": [],
                "deadline": la.deadline.isoformat() if la.deadline else None,
                "submission": submission_data
            })

    return result


from schemas.submission_schema import SubmissionRead
from sqlalchemy.orm import selectinload

# ... (other imports are fine, I will invoke replacement on the specific blocks)

@router.get("/{student_id}/assignments/{assignment_id}/submission", response_model=SubmissionRead)
def get_submission(
    student_id: int,
    assignment_id: int,
    session: Session = Depends(get_session)
):
    # Verify ownership
    assignment = session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    submission = session.exec(
        select(Submission)
        .where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        )
        .options(selectinload(Submission.files), selectinload(Submission.feedback))
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    # Calculate status and timing
    status = "submitted"
    timing = submission.submitted_at
    if submission.updated_at:
        status = "resubmitted"
        timing = submission.updated_at
    if submission.feedback:
        status = "evaluated"
        # timing remains submission.updated_at or submission.submitted_at
        
    return {
        "id": submission.id,
        "description": submission.description,
        "submitted_at": submission.submitted_at,
        "updated_at": submission.updated_at,
        "status": status,
        "timing": timing,
        "files": [
            {"file_name": f.file_name, "file_url": f.file_url}
            for f in submission.files
        ],
        "feedback": {
            "comment": submission.feedback.comment,
            "rating": submission.feedback.rating
        } if submission.feedback else None,
        "audio_url": submission.audio_url
    }


@router.post("/{student_id}/assignments/{assignment_id}/submit", response_model=SubmissionRead)
async def submit_assignment(
    student_id: int,
    assignment_id: int,
    description: str = Form(""),
    submission_method: str = Form("typed"),
    story_grammar_score: Optional[str] = Form(None),
    causal_connective_count: int = Form(0),
    files: Optional[list[UploadFile]] = File(None),
    audio: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    try:
        # Verify ownership
        assignment = session.get(Assignment, assignment_id)
        if not assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")
            
        submission = session.exec(
            select(Submission)
            .where(
                Submission.assignment_id == assignment_id,
                Submission.student_id == student_id
            )
        ).first()

        if not submission:
            submission = Submission(
                assignment_id=assignment_id,
                student_id=student_id,
                description=description,
                submission_method=submission_method,
                story_grammar_score=story_grammar_score,
                causal_connective_count=causal_connective_count,
                submitted_at=datetime.utcnow()
            )
            session.add(submission)
            session.commit()
            session.refresh(submission)
        else:
            # Resubmission logic: Clear old evaluation and files
            # 1. Delete Feedback
            existing_feedback = session.exec(
                select(Feedback).where(Feedback.submission_id == submission.id)
            ).first()
            if existing_feedback:
                session.delete(existing_feedback)
            
            # 2. Delete old SubmissionFile records from DB
            for old_file in submission.files:
                session.delete(old_file)
            
            submission.description = description
            submission.submission_method = submission_method
            submission.story_grammar_score = story_grammar_score
            submission.causal_connective_count = causal_connective_count
            submission.updated_at = datetime.utcnow()
            session.add(submission)
            session.commit()
            session.refresh(submission)

        # Process Files
        if files:
            for file in files:
                safe_filename = f"{submission.id}_{file.filename.replace(' ', '_')}"
                file_path = SUBMISSION_UPLOAD_DIR / safe_filename
                
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                    
                sub_file = SubmissionFile(
                    submission_id=submission.id,
                    file_name=file.filename,
                    file_url=f"/uploads/submissions/{safe_filename}",
                    file_type=file.filename.split('.')[-1]
                )
                session.add(sub_file)
        
        # Process Audio recording
        if audio:
            safe_audio_name = f"audio_{submission.id}_{audio.filename.replace(' ', '_')}"
            audio_path = SUBMISSION_UPLOAD_DIR / safe_audio_name
            
            with open(audio_path, "wb") as f:
                f.write(await audio.read())
            
            submission.audio_url = f"/uploads/submissions/{safe_audio_name}"
            session.add(submission)
        
        session.commit()
        
        submission_refreshed = session.exec(
            select(Submission)
            .where(Submission.id == submission.id)
            .options(selectinload(Submission.files), selectinload(Submission.feedback))
        ).first()
        
        # Calculate status and timing
        status = "submitted"
        timing = submission_refreshed.submitted_at
        if submission_refreshed.updated_at:
            status = "resubmitted"
            timing = submission_refreshed.updated_at
        if submission_refreshed.feedback:
            status = "evaluated"
            # timing remains submission_refreshed.updated_at or submission_refreshed.submitted_at
            
        return {
            "id": submission_refreshed.id,
            "description": submission_refreshed.description,
            "submitted_at": submission_refreshed.submitted_at,
            "updated_at": submission_refreshed.updated_at,
            "status": status,
            "timing": timing,
            "files": [
                {"file_name": f.file_name, "file_url": f.file_url}
                for f in submission_refreshed.files
            ],
            "feedback": {
                "comment": submission_refreshed.feedback.comment,
                "rating": submission_refreshed.feedback.rating
            } if submission_refreshed.feedback else None,
            "audio_url": submission_refreshed.audio_url
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


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





