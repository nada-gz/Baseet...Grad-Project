
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

def migrate_db():
    print(f"🔌 Connecting to database...")
    try:
        if DATABASE_URL.startswith("postgresql+psycopg://"):
             conn_url = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
        else:
             conn_url = DATABASE_URL
             
        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='content_courses' AND column_name='teacher_id';
        """)
        
        if cur.fetchone():
            print("✅ Column 'teacher_id' already exists in 'content_courses'.")
        else:
            print("📦 Adding 'teacher_id' column to 'content_courses'...")
            cur.execute("ALTER TABLE content_courses ADD COLUMN teacher_id INTEGER;")
            cur.execute("CREATE INDEX ix_content_courses_teacher_id ON content_courses (teacher_id);")
            conn.commit()
            print("✅ Column added successfully.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    migrate_db()
