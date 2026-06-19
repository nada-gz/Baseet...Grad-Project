import os
import sys
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import engine

def migrate():
    print("🚀 Starting migration: adding reset password fields to 'users' table...")
    with engine.connect() as conn:
        try:
            # Check reset_token
            check_token = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='reset_token';
            """)
            has_token = conn.execute(check_token).fetchone()
            
            if not has_token:
                print("Adding 'reset_token' column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(255) NULL;"))
                conn.commit()
                print("✅ Added 'reset_token' column.")
            else:
                print("ℹ️ Column 'reset_token' already exists.")
                
            # Check reset_token_expires
            check_expires = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='reset_token_expires';
            """)
            has_expires = conn.execute(check_expires).fetchone()
            
            if not has_expires:
                print("Adding 'reset_token_expires' column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP NULL;"))
                conn.commit()
                print("✅ Added 'reset_token_expires' column.")
            else:
                print("ℹ️ Column 'reset_token_expires' already exists.")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    migrate()
