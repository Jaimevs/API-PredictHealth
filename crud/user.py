from sqlalchemy.orm import Session
from models.user import User
from models.person import Person
from passlib.context import CryptContext
from sqlalchemy import and_

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.ID == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.Correo_Electronico == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.Nombre_Usuario == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).filter(User.Estatus == True).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: dict):
    hashed_password = get_password_hash(user_data["Contrasena"])
    db_user = User(
        Persona_Id=user_data["Persona_Id"],
        Nombre_Usuario=user_data["Nombre_Usuario"],
        Correo_Electronico=user_data["Correo_Electronico"],
        Contrasena=hashed_password,
        Numero_Telefonico_Movil=user_data.get("Numero_Telefonico_Movil"),
        Estatus=user_data.get("Estatus", True)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: dict):
    db_user = db.query(User).filter(User.ID == user_id).first()
    if db_user:
        for key, value in user_data.items():
            if key == "Contrasena" and value:
                value = get_password_hash(value)
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.ID == user_id).first()
    if db_user:
        db_user.Estatus = False
        db.commit()
        db.refresh(db_user)
    return db_user