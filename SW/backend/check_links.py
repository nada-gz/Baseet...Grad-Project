from sqlmodel import Session, text
from db.database import engine

def check_links():
    with engine.connect() as conn:
        print("--- Lessons Linkage ---")
        res = conn.execute(text("SELECT id, content_lesson_id, title FROM lessons"))
        for row in res:
            print(f"ID: {row[0]}, ContentID: {row[1]}, Title: {row[2]}")
            
        print("\n--- Assignments Linkage ---")
        res = conn.execute(text("SELECT id, content_assignment_id, title FROM assignments"))
        for row in res:
            print(f"ID: {row[0]}, ContentID: {row[1]}, Title: {row[2]}")

if __name__ == "__main__":
    check_links()
