from sqlmodel import Session, text
from db.database import engine

def audit():
    with engine.connect() as conn:
        tables = [
            "users", "students", "class_levels", "classrooms", "classroom_course_links", "level_course_links",
            "content_courses", "content_lessons", "content_materials", "content_assignments",
            "courses", "milestones", "lessons", "materials", "assignments",
            "submissions", "submission_files", "feedback", "ask_baseet", "quiz", "quizzes", "quiz_attempts", "log_table"
        ]
        
        print(f"{'Table Name':<25} | {'Count':<6}")
        print("-" * 35)
        for table in tables:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"{table:<25} | {count:<6}")
            except Exception as e:
                print(f"{table:<25} | Error")

if __name__ == "__main__":
    audit()
