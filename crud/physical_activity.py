from sqlalchemy.orm import Session
from models.physical_activity import PhysicalActivity

def get_physical_activity(db: Session, activity_id: int):
    return db.query(PhysicalActivity).filter(PhysicalActivity.ID == activity_id).first()

def get_physical_activities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PhysicalActivity).filter(PhysicalActivity.Estatus == True).offset(skip).limit(limit).all()

def get_physical_activities_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(PhysicalActivity).filter(PhysicalActivity.Usuario_ID == user_id, PhysicalActivity.Estatus == True).offset(skip).limit(limit).all()

def get_physical_activities_by_smartwatch(db: Session, smartwatch_id: int, skip: int = 0, limit: int = 100):
    return db.query(PhysicalActivity).filter(PhysicalActivity.Smartwatch_ID == smartwatch_id, PhysicalActivity.Estatus == True).offset(skip).limit(limit).all()

def create_physical_activity(db: Session, activity_data: dict):
    db_activity = PhysicalActivity(
        Usuario_ID=activity_data["Usuario_ID"],
        Smartwatch_ID=activity_data["Smartwatch_ID"],
        Pasos=activity_data.get("Pasos"),
        Distancia_km=activity_data.get("Distancia_km"),
        Calorias_quemadas=activity_data.get("Calorias_quemadas"),
        Minutos_actividad=activity_data.get("Minutos_actividad"),
        Pisos_subidos=activity_data.get("Pisos_subidos"),
        Estatus=activity_data.get("Estatus", True)
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def update_physical_activity(db: Session, activity_id: int, activity_data: dict):
    db_activity = db.query(PhysicalActivity).filter(PhysicalActivity.ID == activity_id).first()
    if db_activity:
        for key, value in activity_data.items():
            setattr(db_activity, key, value)
        db.commit()
        db.refresh(db_activity)
    return db_activity

def delete_physical_activity(db: Session, activity_id: int):
    db_activity = db.query(PhysicalActivity).filter(PhysicalActivity.ID == activity_id).first()
    if db_activity:
        db_activity.Estatus = False
        db.commit()
        db.refresh(db_activity)
    return db_activity