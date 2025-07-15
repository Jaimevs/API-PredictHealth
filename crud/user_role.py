from sqlalchemy.orm import Session
from models.user_role import UserRole

def get_user_role(db: Session, user_id: int, role_id: int):
    return db.query(UserRole).filter(UserRole.Usuario_ID == user_id, UserRole.Rol_ID == role_id).first()

def get_user_roles(db: Session, user_id: int):
    return db.query(UserRole).filter(UserRole.Usuario_ID == user_id, UserRole.Estatus == True).all()

def get_role_users(db: Session, role_id: int):
    return db.query(UserRole).filter(UserRole.Rol_ID == role_id, UserRole.Estatus == True).all()

def create_user_role(db: Session, user_role_data: dict):
    db_user_role = UserRole(
        Usuario_ID=user_role_data["Usuario_ID"],
        Rol_ID=user_role_data["Rol_ID"],
        Estatus=user_role_data.get("Estatus", True)
    )
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role

def update_user_role(db: Session, user_id: int, role_id: int, user_role_data: dict):
    db_user_role = db.query(UserRole).filter(UserRole.Usuario_ID == user_id, UserRole.Rol_ID == role_id).first()
    if db_user_role:
        for key, value in user_role_data.items():
            setattr(db_user_role, key, value)
        db.commit()
        db.refresh(db_user_role)
    return db_user_role

def delete_user_role(db: Session, user_id: int, role_id: int):
    db_user_role = db.query(UserRole).filter(UserRole.Usuario_ID == user_id, UserRole.Rol_ID == role_id).first()
    if db_user_role:
        db_user_role.Estatus = False
        db.commit()
        db.refresh(db_user_role)
    return db_user_role