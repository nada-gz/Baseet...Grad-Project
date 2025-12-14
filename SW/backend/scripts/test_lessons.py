from db.crud import add_user
from sqlmodel import Session, select
from models.student import Student
from models.lesson import Lesson
from db.database import engine

# 1️⃣ Add a sample user (skip if already exists)
sample_user = add_user(username="nada", email="nada.g.zaki.25@gmail.com", password="nn")
print("Inserted user:", sample_user)

# 2️⃣ Add or get existing student for this user
with Session(engine) as session:
    statement = select(Student).where(Student.user_id == sample_user.id)
    student = session.exec(statement).first()
    if not student:
        # ✅ Let DB generate the ID automatically
        student = Student(user_id=sample_user.id)
        session.add(student)
        session.commit()
        session.refresh(student)
print("Student linked to user:", student)

# 3️⃣ Add a sample lesson linked to the student
with Session(engine) as session:
    statement = select(Lesson).where(
        Lesson.student_id == student.id,
        Lesson.title == "Introduction to Decimals"
    )
    lesson = session.exec(statement).first()
    if not lesson:
        lesson = Lesson(
            student_id=student.id,
            title="Introduction to Decimals",
            number="1",
            progress=20,
            status="in-progress",
            description="Learn the basics of Decimals"
        )
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
print("Inserted lesson:", lesson)

# 4️⃣ Optional: print all lessons
with Session(engine) as session:
    lessons = session.exec(select(Lesson)).all()
    print("All lessons in database:")
    for l in lessons:
        print(l)
