
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
        
        # 1. Update class_levels
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='class_levels' AND column_name='teacher_id';
        """)
        if cur.fetchone():
            print("✅ Column 'teacher_id' already exists in 'class_levels'.")
        else:
            print("📦 Adding 'teacher_id' column to 'class_levels'...")
            cur.execute("ALTER TABLE class_levels ADD COLUMN teacher_id INTEGER;")
            cur.execute("CREATE INDEX ix_class_levels_teacher_id ON class_levels (teacher_id);")
            print("✅ Column added successfully to class_levels.")

        # 2. Update classrooms
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='classrooms' AND column_name='teacher_id';
        """)
        if cur.fetchone():
            print("✅ Column 'teacher_id' already exists in 'classrooms'.")
        else:
            print("📦 Adding 'teacher_id' column to 'classrooms'...")
            cur.execute("ALTER TABLE classrooms ADD COLUMN teacher_id INTEGER;")
            cur.execute("CREATE INDEX ix_classrooms_teacher_id ON classrooms (teacher_id);")
            print("✅ Column added successfully to classrooms.")
            
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    migrate_db()
