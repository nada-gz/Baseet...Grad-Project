from sqlmodel import Session, select
from db.database import engine
from models.material import Material

with Session(engine) as session:
    materials = session.exec(select(Material).where(Material.lesson_id == 1)).all()
    print(materials)
