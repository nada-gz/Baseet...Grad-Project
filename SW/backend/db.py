from sqlmodel import SQLModel, Field, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database connection
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)

# Test model
class TestItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

# Create all tables
def create_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("✅ Tables recreated successfully!")



# Call it when file runs directly
if __name__ == "__main__":
    create_tables()
