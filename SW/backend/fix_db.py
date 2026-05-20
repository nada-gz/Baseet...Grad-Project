from sqlmodel import Session, text
from db.database import engine

def fix():
    with Session(engine) as session:
        try:
            session.exec(text("ALTER TABLE students ADD COLUMN is_flagged BOOLEAN DEFAULT FALSE;"))
            session.commit()
            print("Added is_flagged to students table")
        except Exception as e:
            print("Error altering students table:", repr(e))

if __name__ == "__main__":
    fix()
