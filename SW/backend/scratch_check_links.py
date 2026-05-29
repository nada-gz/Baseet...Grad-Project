from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("--- Users ---")
    users = conn.execute(text("SELECT id, username, role FROM users")).all()
    for u in users:
        print(f"ID: {u.id}, Name: {u.username}, Role: {u.role}")
    
    print("\n--- Students ---")
    students = conn.execute(text("SELECT id, user_id FROM students")).all()
    for s in students:
        print(f"ID: {s.id}, UserID: {s.user_id}")
