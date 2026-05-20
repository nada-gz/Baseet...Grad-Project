import asyncio
from sqlmodel import Session, select
from db.database import engine
from models.user import User, RoleEnum
from routers.supervisor_router import get_all_students_for_supervisor, get_teachers_with_load, get_flagged_students

def test():
    with Session(engine) as session:
        user = session.exec(select(User).where(User.role == RoleEnum.supervisor)).first()
        print("Supervisor:", user)
        if not user:
            print("No supervisor user found!")
            return
            
        try:
            print("Testing /students/all")
            res1 = get_all_students_for_supervisor(session=session, current_user=user)
            print("Result 1:", len(res1))
        except Exception as e:
            print("Error in /students/all:", repr(e))

        try:
            print("Testing /teachers")
            res2 = get_teachers_with_load(session=session, current_user=user)
            print("Result 2:", len(res2))
        except Exception as e:
            print("Error in /teachers:", repr(e))

        try:
            print("Testing /students/flagged")
            res3 = get_flagged_students(session=session, current_user=user)
            print("Result 3:", len(res3))
        except Exception as e:
            print("Error in /students/flagged:", repr(e))

if __name__ == "__main__":
    test()
