from typing import Optional
from sqlmodel import SQLModel

class MaterialBase(SQLModel):
    title: str
    description: Optional[str] = None
    material_type: str
    file_url: str

class MaterialCreate(MaterialBase):
    lesson_id: int

class MaterialRead(MaterialBase):
    id: int
    lesson_id: int
    extracted_text: Optional[str] = None

    class Config:
        from_attributes = True
