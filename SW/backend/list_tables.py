from sqlmodel import Session, text
from db.database import engine

def list_tables():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"))
        for row in res:
            print(row[0])

if __name__ == "__main__":
    list_tables()
