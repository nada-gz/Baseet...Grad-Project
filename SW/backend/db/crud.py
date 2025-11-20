from sqlmodel import select, SQLModel
from .database import engine, Session
from models.user import User
from models.student import Student

# ---------------------------
# Database setup
# ---------------------------

def create_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created successfully!")


# ---------------------------
# User CRUD
# ---------------------------
    
def add_user(username: str, email: str):
    with Session(engine) as session:
        user = User(username=username, email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_all_users():
    with Session(engine) as session:
        statement = select(User)
        results = session.exec(statement)
        return results.all()

def get_user_by_username(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        results = session.exec(statement)
        return results.first()

def get_user_by_id(user_id: int):
    with Session(engine) as session:
        return session.get(User, user_id)

def update_user(user_id: int, username: str, email: str):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        user.username = username
        user.email = email
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        session.delete(user)
        session.commit()
        return user


# ---------------------------
# Student CRUD
# ---------------------------

def create_student(student_data: Student):
    with Session(engine) as session:
        session.add(student_data)
        session.commit()
        session.refresh(student_data)
        return student_data

def get_student_by_id(student_id: int):
    with Session(engine) as session:
        return session.get(Student, student_id)

def get_all_students():
    with Session(engine) as session:
        statement = select(Student)
        results = session.exec(statement)
        return results.all()

def update_student(student_id: int, **kwargs):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            return None
        for key, value in kwargs.items():
            if hasattr(student, key):
                setattr(student, key, value)
        session.add(student)
        session.commit()
        session.refresh(student)
        return student

def delete_student(student_id: int):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            return None
        session.delete(student)
        session.commit()
        return student
    