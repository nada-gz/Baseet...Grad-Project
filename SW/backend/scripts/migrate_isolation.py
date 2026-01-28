
import os
from sqlalchemy import create_engine, text

# Load DB URL
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")

engine = create_engine(DATABASE_URL)

def run_migration():
    with engine.connect() as conn:
        print("Starting Index Migration...")
        
        try:
            # Find unique indexes on content_courses
            result = conn.execute(text("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'content_courses'
                AND indexdef LIKE '%UNIQUE%';
            """))
            indexes = [r[0] for r in result]
            print(f"Found unique indexes: {indexes}")
            
            for idx in indexes:
                if 'course_number' in idx or 'pkey' not in idx: # Safe guard against PK drop if named distinctly
                    print(f"Dropping index: {idx}")
                    conn.execute(text(f"DROP INDEX {idx}"))
                    conn.commit()
                    print("Dropped.")
        except Exception as e:
            print(f"Index drop failed: {e}")
            conn.rollback()
            
        # Also check for Unassigned students
        try:
            print("\nChecking for Unassigned Students...")
            res = conn.execute(text("SELECT count(*) FROM students WHERE classroom_id IS NULL"))
            count = res.scalar()
            print(f"Unassigned Students Count: {count}")
            
            if count == 0:
                print("Creating dummy unassigned student...")
                conn.execute(text("INSERT INTO users (username, email, hashed_password, role, created_at) VALUES ('NewStudent', 'new@student.com', '123', 'student', NOW())"))
                # Get ID
                uid = conn.execute(text("SELECT id FROM users WHERE email='new@student.com'")).scalar()
                conn.execute(text(f"INSERT INTO students (user_id) VALUES ({uid})"))
                conn.commit()
                print("Dummy student created.")
        except Exception as e:
            print(f"Student check failed: {e}")

        print("Migration Finished.")

if __name__ == "__main__":
    run_migration()
