from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select, update
from db.database import engine
from db.crud import (
    create_student,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
    get_lessons,
)
from models.student import Student
from models.lesson import Lesson
from schemas.student_schema import StudentCreate, StudentRead, StudentUpdate
from schemas.lesson_schema import LessonRead, LessonUpdate

# ---------------------------
# Students Router
# ---------------------------
router = APIRouter(prefix="/students", tags=["Students"])

# ---------------------------
# CRUD for Students
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
# Lessons for a Student
# ---------------------------

@router.get("/{student_id}/lessons", response_model=list[LessonRead])
def get_lessons_route(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    lessons = get_lessons(student_id)

    return [
        LessonRead(
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
        for lesson in lessons
    ]


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
        raise HTTPException(status_code=500, detail=str(e))