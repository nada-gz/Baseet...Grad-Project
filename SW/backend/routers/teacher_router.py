from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session, select
from pathlib import Path

from db.database import get_session
from models.content_lesson import ContentLesson
from models.content_material import ContentMaterial
from models.content_course import ContentCourse
from models.student import Student
from models.user import User
from models.class_level import ClassLevel
from models.classroom import Classroom, ClassroomCourseLink
from models.milestone import Milestone
from models.lesson import Lesson
from models.assignment import Assignment
from models.submission import Submission
from models.feedback import Feedback
from models.submission_file import SubmissionFile
from models.content_assignment import ContentAssignment

from schemas.content_schema import (
    ContentLessonRead, ContentCourseRead, ContentCourseCreate, StudentReadWithUser,
    StudentProgressResponse, StudentProgressMilestone, StudentProgressLesson, StudentProgressAssignment,
    ContentAssignmentRead
)
from schemas.classroom_schema import (
    ClassLevelRead, ClassLevelCreate,
    ClassroomRead, ClassroomCreate,
    AssignStudentsRequest, AssignCoursesRequest
)
from typing import List

router = APIRouter(prefix="/teacher", tags=["Teacher"])

UPLOAD_DIR = Path("uploads/content")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------
# Get all courses
# -----------------------
@router.get("/courses", response_model=list[ContentCourseRead])
def get_content_courses(session: Session = Depends(get_session)):
    return session.exec(select(ContentCourse)).all()


# -----------------------
# Create/Update Course
# -----------------------
@router.post("/courses", response_model=ContentCourseRead)
def create_content_course(
    course_data: ContentCourseCreate,
    session: Session = Depends(get_session)
):
    statement = select(ContentCourse).where(ContentCourse.course_number == course_data.course_number)
    existing_course = session.exec(statement).first()

    if existing_course:
        existing_course.description = course_data.description
        session.add(existing_course)
        session.commit()
        session.refresh(existing_course)
        return existing_course

    new_course = ContentCourse(
        course_number=course_data.course_number,
        description=course_data.description
    )
    session.add(new_course)
    session.commit()
    session.refresh(new_course)
    return new_course


# -----------------------
# Get All Students (with Course)
# -----------------------
@router.get("/students", response_model=list[StudentReadWithUser])
def get_all_students(session: Session = Depends(get_session)):
    # Join Student, User, Classroom, and Level
    statement = (
        select(Student, User, Classroom, ClassLevel)
        .join(User, Student.user_id == User.id)
        .outerjoin(Classroom, Student.classroom_id == Classroom.id)
        .outerjoin(ClassLevel, Classroom.level_id == ClassLevel.id)
    )
    results = session.exec(statement).all()
    
    students_list = []
    for student, user, classroom, level in results:
        students_list.append(StudentReadWithUser(
            id=student.id,
            user_id=student.user_id,
            course_number=student.course_number,
            username=user.username,
            email=user.email,
            age=student.age,
            classroom_id=student.classroom_id,
            classroom_name=classroom.name if classroom else None,
            level_name=level.name if level else None,
            status="Active",
            online=False,
            last_access=None,
            state="Stressed" if student.id % 2 == 0 else "Relaxed"
        ))
    return students_list


# -----------------------
# Create content lesson
# -----------------------
@router.post("/lessons", response_model=ContentLessonRead)
def create_content_lesson(
    course_number: int = Form(...),
    milestone_number: int = Form(...),
    lesson_number: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    session: Session = Depends(get_session)
):
    # Check if lesson exists
    statement = select(ContentLesson).where(
        ContentLesson.course_number == course_number,
        ContentLesson.milestone_number == milestone_number,
        ContentLesson.lesson_number == lesson_number
    )
    existing_lesson = session.exec(statement).first()

    if existing_lesson:
        # Update existing
        existing_lesson.title = title
        existing_lesson.description = description
        session.add(existing_lesson)
        session.commit()
        session.refresh(existing_lesson)
        return existing_lesson

    # Create new
    lesson = ContentLesson(
        course_number=course_number,
        milestone_number=milestone_number,
        lesson_number=lesson_number,
        title=title,
        description=description
    )

    session.add(lesson)
    session.commit()
    session.refresh(lesson)

    return lesson


# -----------------------
# Get all content lessons
# -----------------------
@router.get("/lessons", response_model=list[ContentLessonRead])
def get_content_lessons(session: Session = Depends(get_session)):
    return session.exec(select(ContentLesson)).all()


# -----------------------
# Upload content material
# -----------------------
@router.post("/lessons/{lesson_id}/materials")
async def upload_content_material(
    lesson_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    lesson = session.get(ContentLesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    safe_name = f"{lesson_id}_{file.filename.replace(' ', '_')}"
    file_path = UPLOAD_DIR / safe_name

    # Overwrite or write new file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Check if material exists
    statement = select(ContentMaterial).where(
        ContentMaterial.lesson_id == lesson_id,
        ContentMaterial.title == file.filename
    )
    existing_material = session.exec(statement).first()

    if existing_material:
        existing_material.file_url = f"/uploads/content/{safe_name}"
        # Update other fields if necessary, e.g. material_type
        existing_material.material_type = file.filename.split(".")[-1]
        
        session.add(existing_material)
        session.commit()
        session.refresh(existing_material)
        return existing_material

    # Create new material
    material = ContentMaterial(
        lesson_id=lesson_id,
        title=file.filename,
        material_type=file.filename.split(".")[-1],
        file_url=f"/uploads/content/{safe_name}"
    )

    session.add(material)
    session.commit()
    session.refresh(material)

    return material


# -----------------------
# Upload content assignment
# -----------------------
@router.post("/lessons/{lesson_id}/assignments")
async def upload_content_assignment(
    lesson_id: int,
    title: str = Form(...),
    description: str = Form(""),
    assignment_type: str = Form("unknown"),
    file: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    lesson = session.get(ContentLesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    file_url = ""
    if file:
        safe_name = f"assign_{lesson_id}_{file.filename.replace(' ', '_')}"
        file_path = UPLOAD_DIR / safe_name
        with open(file_path, "wb") as f:
            f.write(await file.read())
        file_url = f"/uploads/content/{safe_name}"

    assignment = ContentAssignment(
        lesson_id=lesson_id,
        title=title,
        description=description,
        assignment_type=assignment_type,
        file_url=file_url
    )

    session.add(assignment)
    session.commit()
    session.refresh(assignment)

    return assignment


# -----------------------
# Delete Content Material
# -----------------------
@router.delete("/lessons/{lesson_id}/materials/{material_id}")
def delete_content_material(
    lesson_id: int,
    material_id: int,
    session: Session = Depends(get_session)
):
    material = session.get(ContentMaterial, material_id)
    if not material or material.lesson_id != lesson_id:
        raise HTTPException(404, "Material not found")

    # Optional: Delete file from disk
    # if material.file_url:
    #     file_path = UPLOAD_DIR / material.title
    #     if file_path.exists():
    #         file_path.unlink()

    session.delete(material)
    session.commit()
    return {"ok": True}


# -----------------------
# Delete Lesson
# -----------------------
@router.delete("/lessons/{lesson_id}")
def delete_content_lesson(
    lesson_id: int,
    session: Session = Depends(get_session)
):
    lesson = session.get(ContentLesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    # Manually cascade delete materials
    for material in lesson.materials:
        session.delete(material)

    session.delete(lesson)
    session.commit()
    return {"ok": True}


# -----------------------
# Delete Milestone (Batch)
# -----------------------
@router.delete("/courses/{course_number}/milestones/{milestone_number}")
def delete_content_milestone(
    course_number: int,
    milestone_number: int,
    session: Session = Depends(get_session)
):
    statement = select(ContentLesson).where(
        ContentLesson.course_number == course_number,
        ContentLesson.milestone_number == milestone_number
    )
    lessons = session.exec(statement).all()

    for lesson in lessons:
        for material in lesson.materials:
            session.delete(material)
        session.delete(lesson)
    
    session.commit()
    return {"ok": True}


# -----------------------
# Delete Course (Batch)
# -----------------------
@router.delete("/courses/{course_number}")
def delete_content_course(
    course_number: int,
    session: Session = Depends(get_session)
):
    # Delete lessons (and their materials)
    statement = select(ContentLesson).where(
        ContentLesson.course_number == course_number
    )
    lessons = session.exec(statement).all()

    for lesson in lessons:
        for material in lesson.materials:
            session.delete(material)
        session.delete(lesson)

    # Delete the course metadata
    course_statement = select(ContentCourse).where(ContentCourse.course_number == course_number)
    course_obj = session.exec(course_statement).first()
    if course_obj:
        session.delete(course_obj)

    session.commit()
    return {"ok": True}

# --------------------------
# Class Management
# --------------------------

@router.get("/class-management/levels", response_model=List[ClassLevelRead])
def get_levels(session: Session = Depends(get_session)):
    levels = session.exec(select(ClassLevel)).all()
    # Populate student_count for each classroom manually or via query
    # For simplicity, rely on relationship lazy loading but student_count needs logic
    result = []
    for level in levels:
        classrooms_read = []
        for classroom in level.classrooms:
            classrooms_read.append(ClassroomRead(
                id=classroom.id,
                name=classroom.name,
                level_id=classroom.level_id,
                courses=[ContentCourseRead.from_orm(c) for c in classroom.courses],
                student_count=len(classroom.students)
            ))
        
        result.append(ClassLevelRead(
            id=level.id,
            name=level.name,
            classrooms=classrooms_read
        ))
    return result

@router.post("/class-management/levels", response_model=ClassLevelRead)
def create_level(level_data: ClassLevelCreate, session: Session = Depends(get_session)):
    level = ClassLevel(name=level_data.name)
    session.add(level)
    session.commit()
    session.refresh(level)
    return level


@router.post("/class-management/levels/{level_id}/classrooms", response_model=ClassroomRead)
def create_classroom(level_id: int, classroom_data: ClassroomCreate, session: Session = Depends(get_session)):
    if classroom_data.level_id != level_id:
        raise HTTPException(400, "Level ID mismatch")
    
    classroom = Classroom(name=classroom_data.name, level_id=level_id)
    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    
    return ClassroomRead(
        id=classroom.id,
        name=classroom.name,
        level_id=classroom.level_id,
        student_count=0,
        courses=[]
    )

@router.post("/class-management/classrooms/{classroom_id}/students")
def assign_students(classroom_id: int, req: AssignStudentsRequest, session: Session = Depends(get_session)):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(404, "Classroom not found")

    for student_id in req.student_ids:
        student = session.get(Student, student_id)
        if student:
            student.classroom_id = classroom_id
            session.add(student)
    
    session.commit()
    return {"ok": True}

@router.post("/class-management/classrooms/{classroom_id}/courses")
def assign_courses(classroom_id: int, req: AssignCoursesRequest, session: Session = Depends(get_session)):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(404, "Classroom not found")

    current_course_ids = {c.id for c in classroom.courses}
    
    for course_id in req.course_ids:
        if course_id not in current_course_ids:
            # check if course exists
            course = session.get(ContentCourse, course_id)
            if course:
                classroom.courses.append(course)
    
    session.add(classroom)
    session.commit()
    return {"ok": True}

@router.get("/class-management/unassigned-students", response_model=List[StudentReadWithUser])
def get_unassigned_students(session: Session = Depends(get_session)):
    statement = select(Student, User).join(User).where(Student.classroom_id == None)
    results = session.exec(statement).all()
    
    students_list = []
    for student, user in results:
        students_list.append(StudentReadWithUser(
            id=student.id,
            user_id=student.user_id,
            course_number=student.course_number,
            username=user.username,
            email=user.email,
            age=student.age,
            classroom_id=student.classroom_id 
        ))
    return students_list
    
@router.delete("/class-management/levels/{level_id}")
def delete_level(level_id: int, session: Session = Depends(get_session)):
    level = session.get(ClassLevel, level_id)
    if not level:
        raise HTTPException(404, "Level not found")
    
    # Cascade delete is not set up in models, so manual clean up might be needed or rely on DB
    # For now, let's just delete the level. If there are FK constraints, it might fail.
    # Assuming standard behavior or easy delete for now. 
    # Actually, let's delete classrooms first to be safe if no cascade
    for classroom in level.classrooms:
        # Unassign students
        for student in classroom.students:
            student.classroom_id = None
            session.add(student)
        # Courses link is many-to-many, should auto-remove from link table if defined correctly, 
        # or we might need to purge. 
        # SQLModel usually handles the link table deletion if cascade is set.
        session.delete(classroom)

    session.delete(level)
    session.commit()
    return {"ok": True}

@router.delete("/class-management/classrooms/{classroom_id}/students/{student_id}")
def unassign_student(classroom_id: int, student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student or student.classroom_id != classroom_id:
        raise HTTPException(404, "Student not found in this classroom")
    
    student.classroom_id = None
    session.add(student)
    session.commit()
    return {"ok": True}

@router.delete("/class-management/classrooms/{classroom_id}/courses/{course_id}")
def unassign_course(classroom_id: int, course_id: int, session: Session = Depends(get_session)):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(404, "Classroom not found")
    
    course_to_remove = next((c for c in classroom.courses if c.id == course_id), None)
    if not course_to_remove:
        raise HTTPException(404, "Course not found in this classroom")
    
    classroom.courses.remove(course_to_remove)
    session.add(classroom)
    session.commit()
    return {"ok": True}
@router.delete("/class-management/classrooms/{classroom_id}")
def delete_classroom(classroom_id: int, session: Session = Depends(get_session)):
    classroom = session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(404, "Classroom not found")

    # Unassign all students
    for student in classroom.students:
        student.classroom_id = None
        session.add(student)

    session.delete(classroom)
    session.commit()
    return {"ok": True}

# --------------------------
# Student Progress Deep Dive
# --------------------------

@router.get("/students/{student_id}/progress", response_model=StudentProgressResponse)
def get_student_educational_progress(student_id: int, session: Session = Depends(get_session)):
    # 1. Fetch Student and User
    statement = (
        select(Student, User, Classroom, ClassLevel)
        .join(User, Student.user_id == User.id)
        .outerjoin(Classroom, Student.classroom_id == Classroom.id)
        .outerjoin(ClassLevel, Classroom.level_id == ClassLevel.id)
        .where(Student.id == student_id)
    )
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(404, "Student not found")
    
    student_obj, user_obj, classroom_obj, level_obj = result
    
    student_data = StudentReadWithUser(
        id=student_obj.id,
        user_id=student_obj.user_id,
        username=user_obj.username,
        email=user_obj.email,
        course_number=student_obj.course_number,
        age=student_obj.age,
        classroom_id=student_obj.classroom_id,
        classroom_name=classroom_obj.name if classroom_obj else None,
        level_name=level_obj.name if level_obj else None,
        status="Active",
        online=False,
        last_access=None,
        state="Stressed" if student_obj.id % 2 == 0 else "Relaxed"
    )

    # 2. Get Courses assigned to this student's classroom
    if not student_obj.classroom_id:
        return StudentProgressResponse(student=student_data, milestones=[])

    course_links = session.exec(
        select(ClassroomCourseLink).where(ClassroomCourseLink.classroom_id == student_obj.classroom_id)
    ).all()
    content_course_ids = [link.course_id for link in course_links]
    
    if not content_course_ids:
        return StudentProgressResponse(student=student_data, milestones=[])

    # 3. Fetch all ContentLessons for these courses
    cl_stmt = (
        select(ContentLesson)
        .where(ContentLesson.course_number.in_(content_course_ids))
        .order_by(ContentLesson.course_number, ContentLesson.milestone_number, ContentLesson.lesson_number)
    )
    content_lessons = session.exec(cl_stmt).all()
    
    milestones_resp = []
    # Group by course and milestone using itertools or manual loop
    from itertools import groupby
    for (c_num, m_num), group in groupby(content_lessons, key=lambda x: (x.course_number, x.milestone_number)):
        lessons_progress_list = []
        for cl in group:
            # Check for student's progress record
            lp_stmt = select(Lesson).where(
                Lesson.student_id == student_id,
                Lesson.content_lesson_id == cl.id
            )
            lesson_progress = session.exec(lp_stmt).first()
            
            # Default values
            progress_val = 0
            status_val = "locked"
            lesson_instance_id = cl.id # Fallback
            
            if lesson_progress:
                progress_val = lesson_progress.progress
                status_val = lesson_progress.status
                lesson_instance_id = lesson_progress.id

            # Fetch assignments for this template
            ca_stmt = select(ContentAssignment).where(ContentAssignment.lesson_id == cl.id)
            content_assigns = session.exec(ca_stmt).all()
            
            assign_progress_list = []
            for ca in content_assigns:
                # Check for student's instance
                sa_stmt = select(Assignment).where(
                    Assignment.student_id == student_id,
                    Assignment.content_assignment_id == ca.id
                )
                student_assign = session.exec(sa_stmt).first()
                
                sub_status = "not submitted yet"
                sub_date = None
                feedback_text = None
                rating_val = None
                file_url_val = None
                
                if student_assign:
                    # Fetch submission
                    sub_stmt = select(Submission).where(
                        Submission.assignment_id == student_assign.id,
                        Submission.student_id == student_id
                    ).order_by(Submission.submitted_at.desc())
                    submission = session.exec(sub_stmt).first()
                    
                    if submission:
                        sub_status = "submitted"
                        sub_date = submission.submitted_at
                        
                        feed_stmt = select(Feedback).where(Feedback.submission_id == submission.id)
                        feedback = session.exec(feed_stmt).first()
                        if feedback:
                            sub_status = "evaluated"
                            feedback_text = feedback.comment
                            rating_val = feedback.rating
                        
                        file_stmt = select(SubmissionFile).where(SubmissionFile.submission_id == submission.id)
                        file_obj = session.exec(file_stmt).first()
                        if file_obj:
                            file_url_val = file_obj.file_url

                assign_progress_list.append(StudentProgressAssignment(
                    id=student_assign.id if student_assign else ca.id,
                    title=ca.title,
                    status=sub_status,
                    submission_date=sub_date,
                    feedback=feedback_text,
                    rating=rating_val,
                    file_url=file_url_val,
                    assignment_file_url=ca.file_url
                ))

            lessons_progress_list.append(StudentProgressLesson(
                id=lesson_instance_id,
                title=cl.title,
                status=status_val,
                progress=progress_val,
                assignments=assign_progress_list
            ))

        milestones_resp.append(StudentProgressMilestone(
            milestone_number=m_num,
            course_id=c_num,
            lessons=lessons_progress_list
        ))
    
    return StudentProgressResponse(
        student=student_data,
        milestones=milestones_resp
    )

@router.post("/submissions/{submission_id}/feedback")
def evaluate_submission(
    submission_id: int,
    comment: str = Form(...),
    rating: int = Form(...),
    session: Session = Depends(get_session)
):
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    
    # Check if feedback already exists
    stmt = select(Feedback).where(Feedback.submission_id == submission_id)
    existing_feedback = session.exec(stmt).first()
    
    if existing_feedback:
        existing_feedback.comment = comment
        existing_feedback.rating = rating
        session.add(existing_feedback)
    else:
        new_feedback = Feedback(
            submission_id=submission_id,
            comment=comment,
            rating=rating
        )
        session.add(new_feedback)
    
    session.commit()
    return {"ok": True}
