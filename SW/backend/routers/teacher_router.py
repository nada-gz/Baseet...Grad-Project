from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session, select
from pathlib import Path

from db.database import get_session
from models.content_lesson import ContentLesson
from models.content_material import ContentMaterial
from models.content_level import ContentLevel
from schemas.content_schema import ContentLessonRead, ContentLevelRead, ContentLevelCreate

router = APIRouter(prefix="/teacher", tags=["Teacher"])

UPLOAD_DIR = Path("uploads/content")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------
# Get all levels
# -----------------------
@router.get("/levels", response_model=list[ContentLevelRead])
def get_content_levels(session: Session = Depends(get_session)):
    return session.exec(select(ContentLevel)).all()


# -----------------------
# Create/Update Level
# -----------------------
@router.post("/levels", response_model=ContentLevelRead)
def create_content_level(
    level_data: ContentLevelCreate,
    session: Session = Depends(get_session)
):
    statement = select(ContentLevel).where(ContentLevel.level_number == level_data.level_number)
    existing_level = session.exec(statement).first()

    if existing_level:
        existing_level.description = level_data.description
        session.add(existing_level)
        session.commit()
        session.refresh(existing_level)
        return existing_level

    new_level = ContentLevel(
        level_number=level_data.level_number,
        description=level_data.description
    )
    session.add(new_level)
    session.commit()
    session.refresh(new_level)
    return new_level

# -----------------------
# Create content lesson
# -----------------------
@router.post("/lessons", response_model=ContentLessonRead)
def create_content_lesson(
    level_number: int = Form(...),
    milestone_number: int = Form(...),
    lesson_number: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    session: Session = Depends(get_session)
):
    # Check if lesson exists
    statement = select(ContentLesson).where(
        ContentLesson.level_number == level_number,
        ContentLesson.milestone_number == milestone_number,
        ContentLesson.lesson_number == lesson_number
    )
    existing_lesson = session.exec(statement).first()

    if existing_lesson:
        # Update existing
        existing_lesson.title = title
        existing_lesson.description = description
        session.add(existing_lesson)
        session.commit()
        session.refresh(existing_lesson)
        return existing_lesson

    # Create new
    lesson = ContentLesson(
        level_number=level_number,
        milestone_number=milestone_number,
        lesson_number=lesson_number,
        title=title,
        description=description
    )

    session.add(lesson)
    session.commit()
    session.refresh(lesson)

    return lesson


# -----------------------
# Get all content lessons
# -----------------------
@router.get("/lessons", response_model=list[ContentLessonRead])
def get_content_lessons(session: Session = Depends(get_session)):
    return session.exec(select(ContentLesson)).all()


# -----------------------
# Upload content material
# -----------------------
@router.post("/lessons/{lesson_id}/materials")
async def upload_content_material(
    lesson_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    lesson = session.get(ContentLesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    safe_name = f"{lesson_id}_{file.filename.replace(' ', '_')}"
    file_path = UPLOAD_DIR / safe_name

    # Overwrite or write new file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Check if material exists
    statement = select(ContentMaterial).where(
        ContentMaterial.lesson_id == lesson_id,
        ContentMaterial.title == file.filename
    )
    existing_material = session.exec(statement).first()

    if existing_material:
        existing_material.file_url = f"/uploads/content/{safe_name}"
        # Update other fields if necessary, e.g. material_type
        existing_material.material_type = file.filename.split(".")[-1]
        
        session.add(existing_material)
        session.commit()
        session.refresh(existing_material)
        return existing_material

    # Create new material
    material = ContentMaterial(
        lesson_id=lesson_id,
        title=file.filename,
        material_type=file.filename.split(".")[-1],
        file_url=f"/uploads/content/{safe_name}"
    )

    session.add(material)
    session.commit()
    session.refresh(material)

    return material


# -----------------------
# Delete Content Material
# -----------------------
@router.delete("/lessons/{lesson_id}/materials/{material_id}")
def delete_content_material(
    lesson_id: int,
    material_id: int,
    session: Session = Depends(get_session)
):
    material = session.get(ContentMaterial, material_id)
    if not material or material.lesson_id != lesson_id:
        raise HTTPException(404, "Material not found")

    # Optional: Delete file from disk
    # if material.file_url:
    #     file_path = UPLOAD_DIR / material.title
    #     if file_path.exists():
    #         file_path.unlink()

    session.delete(material)
    session.commit()
    return {"ok": True}


# -----------------------
# Delete Lesson
# -----------------------
@router.delete("/lessons/{lesson_id}")
def delete_content_lesson(
    lesson_id: int,
    session: Session = Depends(get_session)
):
    lesson = session.get(ContentLesson, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    # Manually cascade delete materials
    for material in lesson.materials:
        session.delete(material)

    session.delete(lesson)
    session.commit()
    return {"ok": True}


# -----------------------
# Delete Milestone (Batch)
# -----------------------
@router.delete("/levels/{level_number}/milestones/{milestone_number}")
def delete_content_milestone(
    level_number: int,
    milestone_number: int,
    session: Session = Depends(get_session)
):
    statement = select(ContentLesson).where(
        ContentLesson.level_number == level_number,
        ContentLesson.milestone_number == milestone_number
    )
    lessons = session.exec(statement).all()

    for lesson in lessons:
        for material in lesson.materials:
            session.delete(material)
        session.delete(lesson)
    
    session.commit()
    return {"ok": True}


# -----------------------
# Delete Level (Batch)
# -----------------------
@router.delete("/levels/{level_number}")
def delete_content_level(
    level_number: int,
    session: Session = Depends(get_session)
):
    # Delete lessons (and their materials)
    statement = select(ContentLesson).where(
        ContentLesson.level_number == level_number
    )
    lessons = session.exec(statement).all()

    for lesson in lessons:
        for material in lesson.materials:
            session.delete(material)
        session.delete(lesson)

    # Delete the level metadata
    level_statement = select(ContentLevel).where(ContentLevel.level_number == level_number)
    level_obj = session.exec(level_statement).first()
    if level_obj:
        session.delete(level_obj)

    session.commit()
    return {"ok": True}
