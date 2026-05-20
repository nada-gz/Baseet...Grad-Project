from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    sups = conn.execute(text("SELECT username, email, role FROM users WHERE role = 'supervisor'")).all()
    print(f"Supervisors found: {len(sups)}")
    for s in sups:
        print(f"User: {s.username}, Role: {s.role}")
