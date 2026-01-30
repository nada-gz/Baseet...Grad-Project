
import os
from sqlmodel import Session, select, create_engine
from models.content_course import ContentCourse
from models.student import Student
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")

engine = create_engine(DATABASE_URL)

def diagnose():
    with Session(engine) as session:
        print("--- COURSES ---")
        courses = session.exec(select(ContentCourse)).all()
        for c in courses:
            print(f"ID: {c.id}, Number: {c.course_number}, Title: {c.title}, Teacher: {c.teacher_id}")

        print("\n--- STUDENTS ---")
        students = session.exec(select(Student)).all()
        unassigned_count = 0
        total_count = len(students)
        for s in students:
            if s.classroom_id is None:
                unassigned_count += 1
                print(f"Student {s.id}: Unassigned")
            else:
                print(f"Student {s.id}: Assigned to Classroom {s.classroom_id}")
        
        print(f"\nTotal Students: {total_count}")
        print(f"Unassigned Students: {unassigned_count}")

if __name__ == "__main__":
    diagnose()
