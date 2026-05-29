from sqlmodel import Session, select, text
from db.database import engine
import os

def check():
    with engine.connect() as conn:
        print("Checking content_courses...")
        try:
            conn.execute(text("SELECT title FROM content_courses LIMIT 1"))
            print("  title exists")
        except Exception as e:
            print(f"  title MISSING")

        print("Checking lessons...")
        try:
            conn.execute(text("SELECT content_lesson_id FROM lessons LIMIT 1"))
            print("  content_lesson_id exists")
        except Exception as e:
            print(f"  content_lesson_id MISSING")

        print("Checking assignments...")
        try:
            conn.execute(text("SELECT content_assignment_id FROM assignments LIMIT 1"))
            print("  content_assignment_id exists")
        except Exception as e:
            print(f"  content_assignment_id MISSING")

        print("Checking content_assignments table...")
        try:
            conn.execute(text("SELECT id FROM content_assignments LIMIT 1"))
            print("  table content_assignments EXISTS")
        except Exception as e:
            print(f"  table content_assignments MISSING")

if __name__ == "__main__":
    check()
