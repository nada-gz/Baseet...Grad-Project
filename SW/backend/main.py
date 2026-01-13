import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db.crud import create_tables
from routers.user_router import router as user_router
from routers.student_router import router as student_router
from routers.teacher_router import router as teacher_router
from routers.auth_router import router as auth_router
from routers.dashboard_router import router as dashboard_router
from routers.ai_router import router as ai_router

app = FastAPI(title="My Backend Project")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads folder exists
os.makedirs("uploads/materials", exist_ok=True)

# Mount uploads folder to serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_tables()

# Include routers
app.include_router(user_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(ai_router)

# Root route
@app.get("/")
def read_root():
    return {"message": "Hello from backend"}
