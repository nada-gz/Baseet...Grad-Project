from db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    users = conn.execute(text("SELECT count(*) FROM users")).scalar()
    students = conn.execute(text("SELECT count(*) FROM students")).scalar()
    teachers = conn.execute(text("SELECT count(*) FROM users WHERE role = 'teacher'")).scalar()
    student_roles = conn.execute(text("SELECT count(*) FROM users WHERE role = 'student'")).scalar()
    print(f"Total Users: {users}")
    print(f"Users with role='student': {student_roles}")
    print(f"Users with role='teacher': {teachers}")
    print(f"Rows in 'students' table: {students}")
