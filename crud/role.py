from sqlalchemy.orm import Session
from models.role import Role

def get_role(db: Session, role_id: int):
    return db.query(Role).filter(Role.ID == role_id).first()

def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.Nombre == name).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Role).filter(Role.Estatus == True).offset(skip).limit(limit).all()

def create_role(db: Session, role_data: dict):
    db_role = Role(
        Nombre=role_data["Nombre"],
        Descripcion=role_data.get("Descripcion"),
        Estatus=role_data.get("Estatus", True)
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: int, role_data: dict):
    db_role = db.query(Role).filter(Role.ID == role_id).first()
    if db_role:
        for key, value in role_data.items():
            setattr(db_role, key, value)
        db.commit()
        db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    db_role = db.query(Role).filter(Role.ID == role_id).first()
    if db_role:
        db_role.Estatus = False
        db.commit()
        db.refresh(db_role)
    return db_role