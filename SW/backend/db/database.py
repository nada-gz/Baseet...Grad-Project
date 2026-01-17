import os
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        future=True
    )

def get_session():
    if engine is None:
        raise RuntimeError("Database not available")
    with Session(engine) as session:
        yield session
