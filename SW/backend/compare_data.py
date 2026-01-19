from sqlalchemy import text
from db.database import engine

def compare():
    with engine.connect() as conn:
        print("--- Courses ---")
        try:
            res = conn.execute(text("SELECT * FROM courses"))
            for row in res:
                print(f"Legacy: {row._mapping}")
        except Exception as e:
            print(f"Error courses: {e}")

        try:
            res = conn.execute(text("SELECT * FROM content_courses"))
            for row in res:
                print(f"Content: {row._mapping}")
        except Exception as e:
            print(f"Error content_courses: {e}")
        
        print("\n--- Materials ---")
        try:
            res = conn.execute(text("SELECT * FROM materials"))
            for row in res:
                print(f"Legacy Material: {row._mapping}")
        except Exception as e:
            print(f"Error materials: {e}")

        try:
            res = conn.execute(text("SELECT * FROM content_materials"))
            for row in res:
                print(f"Content Material: {row._mapping}")
        except Exception as e:
            print(f"Error content_materials: {e}")

if __name__ == "__main__":
    compare()
