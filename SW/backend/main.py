import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.crud import create_tables
from routers.user_router import router as user_router
from routers.student_router import router as student_router
from routers.auth_router import router as auth_router

app = FastAPI(title="My Backend Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
# Set RESET_DB=true in environment to drop and recreate all tables
# By default, tables are only created if they don't exist (preserves data)
reset_db = os.getenv("RESET_DB", "false").lower() == "true"
create_tables(drop_existing=reset_db)

# Include routers
app.include_router(user_router)
app.include_router(student_router)
app.include_router(auth_router)

# Root route
@app.get("/")
def read_root():
    return {"message": "Hello from backend"}
