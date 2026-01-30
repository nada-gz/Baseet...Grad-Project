import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def restore_content(email="nada.g.z@gmail.com"):
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    # Handle psycopg2 vs psycopg preference
    db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # 1. Get Teacher ID
        result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
        if not result:
            print(f"User with email {email} not found.")
            return
        
        teacher_id = result[0]
        print(f"Found teacher {email} with ID: {teacher_id}")

        # 2. Update Content Courses
        res = conn.execute(text("UPDATE content_courses SET teacher_id = :tid WHERE teacher_id IS NULL"), {"tid": teacher_id})
        print(f"Updated {res.rowcount} content_courses.")

        # 3. Update Content Lessons
        res = conn.execute(text("UPDATE content_lessons SET teacher_id = :tid WHERE teacher_id IS NULL"), {"tid": teacher_id})
        print(f"Updated {res.rowcount} content_lessons.")

        # 4. Update Class Levels
        res = conn.execute(text("UPDATE class_levels SET teacher_id = :tid WHERE teacher_id IS NULL"), {"tid": teacher_id})
        print(f"Updated {res.rowcount} class_levels.")

        # 5. Update Classrooms
        res = conn.execute(text("UPDATE classrooms SET teacher_id = :tid WHERE teacher_id IS NULL"), {"tid": teacher_id})
        print(f"Updated {res.rowcount} classrooms.")

        conn.commit()
        print("Migration complete!")

if __name__ == "__main__":
    restore_content()
