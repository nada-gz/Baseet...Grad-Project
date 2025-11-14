from fastapi import FastAPI
from db.crud import create_tables
from routers.user_router import router as user_router

app = FastAPI(title="My Backend Project")

# Create tables on startup
create_tables()

# Include routers
app.include_router(user_router)

# Root route
@app.get("/")
def read_root():
    return {"message": "Hello from backend"}
