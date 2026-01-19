from sqlalchemy import text
from db.database import engine

def find_matches():
    titles = ["الهضاب", "البناء الضوئي", "الطاقة"]
    with engine.connect() as conn:
        for title in titles:
            stmt = text("SELECT id FROM content_lessons WHERE title = :title")
            res = conn.execute(stmt, {"title": title}).first()
            if res:
                print(f"Match found for '{title}': ContentID {res[0]}")
            else:
                print(f"No match found for '{title}'")

if __name__ == "__main__":
    find_matches()
