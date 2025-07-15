from sqlalchemy.orm import Session
from models.heart_measurement import HeartMeasurement

def get_heart_measurement(db: Session, measurement_id: int):
    return db.query(HeartMeasurement).filter(HeartMeasurement.ID == measurement_id).first()

def get_heart_measurements(db: Session, skip: int = 0, limit: int = 100):
    return db.query(HeartMeasurement).filter(HeartMeasurement.Estatus == True).offset(skip).limit(limit).all()

def get_heart_measurements_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(HeartMeasurement).filter(HeartMeasurement.Usuario_ID == user_id, HeartMeasurement.Estatus == True).offset(skip).limit(limit).all()

def get_heart_measurements_by_smartwatch(db: Session, smartwatch_id: int, skip: int = 0, limit: int = 100):
    return db.query(HeartMeasurement).filter(HeartMeasurement.Smartwatch_ID == smartwatch_id, HeartMeasurement.Estatus == True).offset(skip).limit(limit).all()

def create_heart_measurement(db: Session, measurement_data: dict):
    db_measurement = HeartMeasurement(
        Usuario_ID=measurement_data["Usuario_ID"],
        Smartwatch_ID=measurement_data["Smartwatch_ID"],
        Timestamp_medicion=measurement_data["Timestamp_medicion"],
        Frecuencia_cardiaca=measurement_data["Frecuencia_cardiaca"],
        Presion_sistolica=measurement_data.get("Presion_sistolica"),
        Presion_diastolica=measurement_data.get("Presion_diastolica"),
        Saturacion_oxigeno=measurement_data.get("Saturacion_oxigeno"),
        Temperatura=measurement_data.get("Temperatura"),
        Nivel_estres=measurement_data.get("Nivel_estres"),
        Variabilidad_ritmo=measurement_data.get("Variabilidad_ritmo"),
        Estatus=measurement_data.get("Estatus", True)
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def update_heart_measurement(db: Session, measurement_id: int, measurement_data: dict):
    db_measurement = db.query(HeartMeasurement).filter(HeartMeasurement.ID == measurement_id).first()
    if db_measurement:
        for key, value in measurement_data.items():
            setattr(db_measurement, key, value)
        db.commit()
        db.refresh(db_measurement)
    return db_measurement

def delete_heart_measurement(db: Session, measurement_id: int):
    db_measurement = db.query(HeartMeasurement).filter(HeartMeasurement.ID == measurement_id).first()
    if db_measurement:
        db_measurement.Estatus = False
        db.commit()
        db.refresh(db_measurement)
    return db_measurement