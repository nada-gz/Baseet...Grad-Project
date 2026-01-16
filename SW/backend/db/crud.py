# crud.py
from sqlmodel import select, SQLModel, Session, update
from .database import engine
from models.user import User, RoleEnum
from models.student import Student
from models.course import Course
from models.milestone import Milestone
from models.lesson import Lesson
from models.material import Material
from models.assignment import Assignment
from models.submission import Submission
from models.submission_file import SubmissionFile
from models.feedback import Feedback
from models.quiz import Quiz
from models.ask_baseet import AskBaseet
from models.log import Log
from models.content_lesson import ContentLesson
from models.content_material import ContentMaterial
from models.content_course import ContentCourse
from models.class_level import ClassLevel
from models.classroom import Classroom, ClassroomCourseLink
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
# Course CRUD
# ---------------------------

def get_courses():
    with Session(engine) as session:
        return session.exec(select(Course)).all()

def create_course(course: Course):
    with Session(engine) as session:
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

# ---------------------------
# Milestones CRUD
# ---------------------------

def get_milestones(student_id: int, course_id: int = None):
    with Session(engine) as session:
        query = select(Milestone).where(Milestone.student_id == student_id)
        if course_id:
            query = query.where(Milestone.course_id == course_id)
        query = query.order_by(Milestone.number)
        return session.exec(query).all()


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
        statement = select(Lesson).join(Milestone).where(Lesson.student_id == student_id).order_by(Milestone.number, Lesson.lesson_number)
        return session.exec(statement).all()


def get_lesson_by_id(lesson_id: int):
    with Session(engine) as session:
        return session.get(Lesson, lesson_id)


def get_lessons_by_milestone(milestone_number: int):
    with Session(engine) as session:
        statement = select(Lesson).join(Milestone).where(Milestone.number == milestone_number).order_by(Lesson.lesson_number)
        return session.exec(statement).all()


def get_lessons_grouped_by_milestones(student_id: int):
    milestones = get_milestones(student_id)
    lessons = get_lessons(student_id)
    result = []
    for milestone in milestones:
        milestone_lessons = [lesson for lesson in lessons if lesson.milestone_id == milestone.id]
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
    
def get_assignments_by_lesson(lesson_id: int):
    with Session(engine) as session:
        return session.exec(
            select(Assignment).where(Assignment.lesson_id == lesson_id)
        ).all()


def get_assignment_by_id(assignment_id: int):
    with Session(engine) as session:
        return session.get(Assignment, assignment_id)


def create_assignment(assignment: Assignment):
    with Session(engine) as session:
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
    

def get_submission(student_id: int, assignment_id: int):
    with Session(engine) as session:
        return session.exec(
            select(Submission)
            .where(
                Submission.student_id == student_id,
                Submission.assignment_id == assignment_id
            )
        ).first()


def create_submission(student_id: int, assignment_id: int, description: str | None):
    with Session(engine) as session:
        submission = Submission(
            student_id=student_id,
            assignment_id=assignment_id,
            description=description
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        return submission


def update_submission(submission: Submission, description: str | None):
    with Session(engine) as session:
        submission.description = description
        submission.updated_at = datetime.utcnow()
        session.add(submission)
        session.commit()
        session.refresh(submission)
        return submission


def replace_submission_files(submission_id: int, files: list[dict]):
    """
    files = [{file_name, file_url}]
    """
    with Session(engine) as session:
        session.exec(
            select(SubmissionFile)
            .where(SubmissionFile.submission_id == submission_id)
        ).delete()

        for f in files:
            session.add(
                SubmissionFile(
                    submission_id=submission_id,
                    file_name=f["file_name"],
                    file_url=f["file_url"]
                )
            )

        session.commit()


def get_feedback(submission_id: int):
    with Session(engine) as session:
        return session.exec(
            select(Feedback)
            .where(Feedback.submission_id == submission_id)
        ).first()


def create_or_update_feedback(submission_id: int, comment: str, rating: int | None):
    with Session(engine) as session:
        feedback = session.exec(
            select(Feedback)
            .where(Feedback.submission_id == submission_id)
        ).first()

        if feedback:
            feedback.comment = comment
            feedback.rating = rating
        else:
            feedback = Feedback(
                submission_id=submission_id,
                comment=comment,
                rating=rating
            )
            session.add(feedback)

        session.commit()
        session.refresh(feedback)
        return feedback
    
def get_assignments_with_submission(student_id: int, lesson_id: int):
    """
    Returns assignments + submission + files + feedback
    """
    with Session(engine) as session:
        assignments = session.exec(
            select(Assignment).where(Assignment.lesson_id == lesson_id)
        ).all()

        for assignment in assignments:
            submission = session.exec(
                select(Submission)
                .where(
                    Submission.assignment_id == assignment.id,
                    Submission.student_id == student_id
                )
            ).first()

            assignment.submission = submission

        return assignments
    
