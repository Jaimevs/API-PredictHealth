from sqlalchemy.orm import Session
from models.health_profile import HealthProfile

def get_health_profile(db: Session, profile_id: int):
    return db.query(HealthProfile).filter(HealthProfile.ID == profile_id).first()

def get_health_profile_by_user(db: Session, user_id: int):
    return db.query(HealthProfile).filter(HealthProfile.Usuario_ID == user_id).first()

def get_health_profiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(HealthProfile).filter(HealthProfile.Estatus == True).offset(skip).limit(limit).all()

def create_health_profile(db: Session, profile_data: dict):
    db_profile = HealthProfile(
        Usuario_ID=profile_data["Usuario_ID"],
        Peso_kg=profile_data.get("Peso_kg"),
        Altura_cm=profile_data.get("Altura_cm"),
        Tipo_sangre=profile_data.get("Tipo_sangre"),
        Fumador=profile_data.get("Fumador", False),
        Diabetico=profile_data.get("Diabetico", False),
        Hipertenso=profile_data.get("Hipertenso", False),
        Historial_cardiaco=profile_data.get("Historial_cardiaco", False),
        Estatus=profile_data.get("Estatus", True)
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def update_health_profile(db: Session, profile_id: int, profile_data: dict):
    db_profile = db.query(HealthProfile).filter(HealthProfile.ID == profile_id).first()
    if db_profile:
        for key, value in profile_data.items():
            setattr(db_profile, key, value)
        db.commit()
        db.refresh(db_profile)
    return db_profile

def delete_health_profile(db: Session, profile_id: int):
    db_profile = db.query(HealthProfile).filter(HealthProfile.ID == profile_id).first()
    if db_profile:
        db_profile.Estatus = False
        db.commit()
        db.refresh(db_profile)
    return db_profile