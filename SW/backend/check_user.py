from db.database import engine
from sqlmodel import Session, select
from models.student import Student
from models.user import User

with Session(engine) as session:
    student = session.get(Student, 1)
    if student:
        user = session.get(User, student.user_id)
        print("Student 1:", user.username)
