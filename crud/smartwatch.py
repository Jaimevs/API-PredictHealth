from sqlalchemy.orm import Session
from models.smartwatch import Smartwatch

def get_smartwatch(db: Session, smartwatch_id: int):
    return db.query(Smartwatch).filter(Smartwatch.ID == smartwatch_id).first()

def get_smartwatch_by_serial(db: Session, serial: str):
    return db.query(Smartwatch).filter(Smartwatch.Numero_serie == serial).first()

def get_smartwatches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Smartwatch).filter(Smartwatch.Estatus == True).offset(skip).limit(limit).all()

def get_smartwatches_by_user(db: Session, user_id: int):
    return db.query(Smartwatch).filter(Smartwatch.Usuario_ID == user_id, Smartwatch.Estatus == True).all()

def create_smartwatch(db: Session, smartwatch_data: dict):
    db_smartwatch = Smartwatch(
        Usuario_ID=smartwatch_data["Usuario_ID"],
        Marca=smartwatch_data["Marca"],
        Modelo=smartwatch_data["Modelo"],
        Numero_serie=smartwatch_data["Numero_serie"],
        Fecha_vinculacion=smartwatch_data.get("Fecha_vinculacion"),
        Activo=smartwatch_data.get("Activo", True),
        Estatus=smartwatch_data.get("Estatus", True)
    )
    db.add(db_smartwatch)
    db.commit()
    db.refresh(db_smartwatch)
    return db_smartwatch

def update_smartwatch(db: Session, smartwatch_id: int, smartwatch_data: dict):
    db_smartwatch = db.query(Smartwatch).filter(Smartwatch.ID == smartwatch_id).first()
    if db_smartwatch:
        for key, value in smartwatch_data.items():
            setattr(db_smartwatch, key, value)
        db.commit()
        db.refresh(db_smartwatch)
    return db_smartwatch

def delete_smartwatch(db: Session, smartwatch_id: int):
    db_smartwatch = db.query(Smartwatch).filter(Smartwatch.ID == smartwatch_id).first()
    if db_smartwatch:
        db_smartwatch.Estatus = False
        db.commit()
        db.refresh(db_smartwatch)
    return db_smartwatch