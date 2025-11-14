from sqlmodel import select
from .database import engine, Session
from ..models.user import User

def create_tables():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created successfully!")

def add_user(name: str, age: int):
    with Session(engine) as session:
        user = User(name=name, age=age)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_all_users():
    with Session(engine) as session:
        statement = select(User)
        results = session.exec(statement)
        return results.all()

def get_user_by_name(name: str):
    with Session(engine) as session:
        statement = select(User).where(User.name == name)
        results = session.exec(statement)
        return results.first()

def get_user_by_id(user_id: int):
    with Session(engine) as session:
        return session.get(User, user_id)

def update_user(user_id: int, name: str, age: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            return None
        user.name = name
        user.age = age
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
