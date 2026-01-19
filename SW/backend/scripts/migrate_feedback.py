import os
import sys
from sqlalchemy import text
from sqlmodel import create_engine

# Add parent directory to sys.path to find db mapping if needed, 
# but we can just use the engine from db.database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import engine

def migrate():
    print("🚀 Starting migration: adding 'created_at' to 'feedback' table...")
    with engine.connect() as conn:
        try:
            # Check if column exists first (Postgres way)
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='feedback' AND column_name='created_at';
            """)
            result = conn.execute(check_query).fetchone()
            
            if not result:
                print("Adding 'created_at' column...")
                conn.execute(text("ALTER TABLE feedback ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
                conn.commit()
                print("✅ Migration successful!")
            else:
                print("ℹ️ Column 'created_at' already exists.")
        except Exception as e:
            print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    migrate()
