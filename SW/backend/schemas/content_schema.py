from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel



class ContentCourseRead(BaseModel):
    id: int
    course_number: int
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ContentCourseCreate(BaseModel):
    course_number: int
    title: Optional[str] = None
    description: Optional[str] = None


class ContentMaterialRead(BaseModel):
    id: int
    lesson_id: int
    title: str
    file_url: str
    material_type: str

    class Config:
        from_attributes = True

class StudentReadWithUser(BaseModel):
    id: int
    user_id: int
    username: str
    email: str
    course_number: Optional[int] = None
    age: Optional[int] = None
    classroom_id: Optional[int] = None
    classroom_name: Optional[str] = None
    level_name: Optional[str] = None
    status: Optional[str] = "Active"
    online: bool = False
    last_access: Optional[datetime] = None
    state: Optional[str] = "Relaxed"
    progress: Optional[int] = 0

    class Config:
        from_attributes = True

class StudentProgressAssignment(BaseModel):
    id: int
    title: str
    status: str # "not submitted yet", "submitted", "evaluated", "resubmitted"
    submission_id: Optional[int] = None # Added for evaluation
    submission_date: Optional[datetime] = None
    timing: Optional[datetime] = None # Relevant timestamp for the current status
    feedback: Optional[str] = None
    rating: Optional[int] = None
    submission_method: Optional[str] = None
    story_grammar_score: Optional[str] = None
    causal_connective_count: Optional[int] = None
    audio_url: Optional[str] = None
    file_url: Optional[str] = None
    assignment_file_url: Optional[str] = None
    deadline: Optional[datetime] = None

class StudentProgressLesson(BaseModel):
    id: int
    title: str
    status: str # "completed", "in-progress", "locked"
    progress: int
    assignments: List[StudentProgressAssignment] = []

class StudentProgressMilestone(BaseModel):
    milestone_number: int
    course_id: Optional[int] = None
    lessons: List[StudentProgressLesson] = []

class StudentProgressResponse(BaseModel):
    student: StudentReadWithUser
    milestones: List[StudentProgressMilestone] = []


class ContentAssignmentFileRead(BaseModel):
    id: int
    assignment_id: int
    file_url: str
    file_name: str

    class Config:
        from_attributes = True


class ContentAssignmentRead(BaseModel):
    id: int
    lesson_id: int
    title: str
    description: Optional[str] = None
    assignment_type: str
    file_url: str
    deadline: Optional[datetime] = None
    files: List[ContentAssignmentFileRead] = []

    class Config:
        from_attributes = True


class ContentLessonRead(BaseModel):
    id: int
    course_number: int
    milestone_number: int
    lesson_number: int
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    materials: List[ContentMaterialRead] = []
    assignments: List[ContentAssignmentRead] = []

    class Config:
        from_attributes = True


class ContentLessonCreate(BaseModel):
    course_number: int
    milestone_number: int
    lesson_number: int
    title: str
    duration_minutes: Optional[int] = 20
