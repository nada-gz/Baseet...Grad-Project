from sqlmodel import SQLModel

# Resolve forward refs
from models.material import Material
from models.lesson import Lesson

Material.update_forward_refs()
Lesson.update_forward_refs()
