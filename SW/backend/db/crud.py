# crud.py
from sqlmodel import select, SQLModel, Session
from .database import engine
from models.user import User, RoleEnum
from models.student import Student
from utils.auth import hash_password

# ---------------------------
# Database setup
# ---------------------------

def create_tables(drop_existing: bool = False):
    """
    Create database tables.
    
    Args:
        drop_existing: If True, drops all existing tables before creating new ones.
                      If False (default), only creates tables that don't exist.
    """
    if drop_existing:
        SQLModel.metadata.drop_all(engine)
        print("⚠️  Dropped all existing tables!")
    
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created/verified successfully!")


# ---------------------------
# User CRUD
# ---------------------------

def add_user(username: str, email: str, password: str, role: RoleEnum = RoleEnum.student):
    with Session(engine) as session:
        hashed = hash_password(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed,
            role=role
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_all_users():
    with Session(engine) as session:
        statement = select(User)
        return session.exec(statement).all()


def get_user_by_username(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()


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
        return session.exec(statement).all()


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
