# crud.py
from sqlmodel import select, SQLModel, Session, update
from .database import engine
from models.user import User, RoleEnum
from models.student import Student
from models.milestone import Milestone
from models.lesson import Lesson
from models.material import Material
from models.assignment import Assignment
from models.quiz import Quiz
from models.ask_baseet import AskBaseet
from utils.auth import hash_password
from datetime import datetime

def create_tables():
    SQLModel.metadata.create_all(engine)
    print("✅ PostgreSQL tables ready!")


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


# ---------------------------
# Milestones CRUD
# ---------------------------

def get_milestones(student_id: int):
    with Session(engine) as session:
        statement = select(Milestone).where(Milestone.student_id == student_id).order_by(Milestone.number)
        return session.exec(statement).all()


def get_milestone_by_id(milestone_id: int):
    with Session(engine) as session:
        return session.get(Milestone, milestone_id)


def create_milestone(milestone_data: Milestone):
    with Session(engine) as session:
        session.add(milestone_data)
        session.commit()
        session.refresh(milestone_data)
        return milestone_data


def update_milestone(milestone_id: int, **kwargs):
    with Session(engine) as session:
        milestone = session.get(Milestone, milestone_id)
        if not milestone:
            return None
        for key, value in kwargs.items():
            if hasattr(milestone, key):
                setattr(milestone, key, value)
        session.add(milestone)
        session.commit()
        session.refresh(milestone)
        return milestone


def delete_milestone(milestone_id: int):
    with Session(engine) as session:
        milestone = session.get(Milestone, milestone_id)
        if not milestone:
            return None
        session.delete(milestone)
        session.commit()
        return milestone


# ---------------------------
# Lessons CRUD
# ---------------------------

def get_lessons(student_id: int):
    with Session(engine) as session:
        statement = select(Lesson).where(Lesson.student_id == student_id).order_by(Lesson.milestone_number, Lesson.lesson_number)
        return session.exec(statement).all()


def get_lesson_by_id(lesson_id: int):
    with Session(engine) as session:
        return session.get(Lesson, lesson_id)


def get_lessons_by_milestone(milestone_number: int):
    with Session(engine) as session:
        statement = select(Lesson).where(Lesson.milestone_number == milestone_number).order_by(Lesson.lesson_number)
        return session.exec(statement).all()


def get_lessons_grouped_by_milestones(student_id: int):
    milestones = get_milestones(student_id)
    lessons = get_lessons(student_id)
    result = []
    for milestone in milestones:
        milestone_lessons = [lesson for lesson in lessons if lesson.milestone_number == milestone.id]
        result.append({"milestone": milestone, "lessons": milestone_lessons})
    return result


def create_lesson(lesson_data: Lesson):
    with Session(engine) as session:
        session.add(lesson_data)
        session.commit()
        session.refresh(lesson_data)
        return lesson_data


def update_lesson(lesson: Lesson):
    with Session(engine) as session:
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        return lesson


# ---------------------------
# Materials CRUD
# ---------------------------

def get_materials(student_id: int):
    with Session(engine) as session:
        statement = select(Material).where(Material.student_id == student_id)
        return session.exec(statement).all()


def get_material_by_id(material_id: int):
    with Session(engine) as session:
        return session.get(Material, material_id)


def create_material(material_data: Material):
    with Session(engine) as session:
        session.add(material_data)
        session.commit()
        session.refresh(material_data)
        return material_data


def update_material(material_id: int, **kwargs):
    with Session(engine) as session:
        material = session.get(Material, material_id)
        if not material:
            return None
        for key, value in kwargs.items():
            if hasattr(material, key):
                setattr(material, key, value)
        session.add(material)
        session.commit()
        session.refresh(material)
        return material


def delete_material(material_id: int):
    with Session(engine) as session:
        material = session.get(Material, material_id)
        if not material:
            return None
        session.delete(material)
        session.commit()
        return material


# ---------------------------
# Assignments CRUD
# ---------------------------

def get_assignments(student_id: int):
    with Session(engine) as session:
        statement = select(Assignment).where(Assignment.student_id == student_id)
        return session.exec(statement).all()


def get_assignment_by_id(assignment_id: int):
    with Session(engine) as session:
        return session.get(Assignment, assignment_id)


def create_assignment(assignment_data: Assignment):
    with Session(engine) as session:
        session.add(assignment_data)
        session.commit()
        session.refresh(assignment_data)
        return assignment_data


def update_assignment(assignment_id: int, **kwargs):
    with Session(engine) as session:
        assignment = session.get(Assignment, assignment_id)
        if not assignment:
            return None
        for key, value in kwargs.items():
            if hasattr(assignment, key):
                setattr(assignment, key, value)
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment


def delete_assignment(assignment_id: int):
    with Session(engine) as session:
        assignment = session.get(Assignment, assignment_id)
        if not assignment:
            return None
        session.delete(assignment)
        session.commit()
        return assignment


# ---------------------------
# Quizzes CRUD
# ---------------------------

def get_quizzes(student_id: int):
    with Session(engine) as session:
        statement = select(Quiz).where(Quiz.student_id == student_id)
        return session.exec(statement).all()


def get_quiz_by_id(quiz_id: int):
    with Session(engine) as session:
        return session.get(Quiz, quiz_id)


def create_quiz(quiz_data: Quiz):
    with Session(engine) as session:
        session.add(quiz_data)
        session.commit()
        session.refresh(quiz_data)
        return quiz_data


def update_quiz(quiz_id: int, **kwargs):
    with Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if not quiz:
            return None
        for key, value in kwargs.items():
            if hasattr(quiz, key):
                setattr(quiz, key, value)
        session.add(quiz)
        session.commit()
        session.refresh(quiz)
        return quiz


def delete_quiz(quiz_id: int):
    with Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if not quiz:
            return None
        session.delete(quiz)
        session.commit()
        return quiz


# ---------------------------
# Ask Baseet CRUD
# ---------------------------

def get_ask_baseet_conversations(student_id: int):
    with Session(engine) as session:
        statement = select(AskBaseet).where(AskBaseet.student_id == student_id)
        return session.exec(statement).all()


def get_ask_baseet_by_id(ask_baseet_id: int):
    with Session(engine) as session:
        return session.get(AskBaseet, ask_baseet_id)


def create_ask_baseet(ask_baseet_data: AskBaseet):
    with Session(engine) as session:
        session.add(ask_baseet_data)
        session.commit()
        session.refresh(ask_baseet_data)
        return ask_baseet_data


def update_ask_baseet(ask_baseet_id: int, **kwargs):
    with Session(engine) as session:
        ask_baseet = session.get(AskBaseet, ask_baseet_id)
        if not ask_baseet:
            return None
        for key, value in kwargs.items():
            if hasattr(ask_baseet, key):
                setattr(ask_baseet, key, value)
        session.add(ask_baseet)
        session.commit()
        session.refresh(ask_baseet)
        return ask_baseet


def delete_ask_baseet(ask_baseet_id: int):
    with Session(engine) as session:
        ask_baseet = session.get(AskBaseet, ask_baseet_id)
        if not ask_baseet:
            return None
        session.delete(ask_baseet)
        session.commit()
        return ask_baseet
