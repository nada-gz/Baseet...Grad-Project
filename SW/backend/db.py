from sqlmodel import SQLModel, Field, create_engine

# 1️ Define your database URL — this will create a SQLite file
DATABASE_URL = "sqlite:///./test.db"

# 2️ Create an engine (connects Python to the database)
engine = create_engine(DATABASE_URL, echo=True)

# 3️ Define a simple test model
class TestItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

# 4️ Create tables function
def create_tables():
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()
