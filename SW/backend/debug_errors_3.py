import sys
from sqlmodel import Session, create_engine, select
from db.database import engine
from routers.teacher_router import get_student_educational_progress
from routers.student_router import get_lesson_assignments
from models.student import Student
from models.lesson import Lesson
from models.assignment import Assignment

with open("debug_output_3.txt", "w") as f:
    def log(msg):
        f.write(str(msg) + "\n")
        print(msg)

    log("--- Debugging Teacher Progress ---")
    try:
        with Session(engine) as session:
            student = session.exec(select(Student)).first()
            if not student:
                log("No students found.")
            else:
                log(f"Testing for Student ID: {student.id}")
                try:
                    res = get_student_educational_progress(student_id=student.id, session=session)
                    log(f"Teacher Progress Success! Result keys: {res.dict().keys()}")
                except Exception as e:
                    log("FAILED teacher_router:")
                    import traceback
                    traceback.print_exc(file=f)
    except Exception as e:
         log(f"Session Error: {e}")

    log("\n--- Debugging Student Assignments ---")
    try:
        with Session(engine) as session:
            assignment = session.exec(select(Assignment)).first()
            if not assignment:
                log("No assignments found.")
            else:
                log(f"Testing for Student ID: {assignment.student_id}, Lesson ID: {assignment.lesson_id}")
                try:
                    res = get_lesson_assignments(student_id=assignment.student_id, lesson_id=assignment.lesson_id, session=session)
                    log(f"Student Assignments Success! Found {len(res)} assignments.")
                except Exception as e:
                    log("FAILED student_router:")
                    import traceback
                    traceback.print_exc(file=f)
    except Exception as e:
         log(f"Session Error: {e}")
