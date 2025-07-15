from sqlalchemy.orm import Session
from models.alert import Alert

def get_alert(db: Session, alert_id: int):
    return db.query(Alert).filter(Alert.ID == alert_id).first()

def get_alerts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Alert).filter(Alert.Estatus == True).offset(skip).limit(limit).all()

def get_alerts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Alert).filter(Alert.Usuario_ID == user_id, Alert.Estatus == True).offset(skip).limit(limit).all()

def get_alerts_by_smartwatch(db: Session, smartwatch_id: int, skip: int = 0, limit: int = 100):
    return db.query(Alert).filter(Alert.Smartwatch_ID == smartwatch_id, Alert.Estatus == True).offset(skip).limit(limit).all()

def get_alerts_by_priority(db: Session, priority: str, skip: int = 0, limit: int = 100):
    return db.query(Alert).filter(Alert.Prioridad == priority, Alert.Estatus == True).offset(skip).limit(limit).all()

def create_alert(db: Session, alert_data: dict):
    db_alert = Alert(
        Usuario_ID=alert_data["Usuario_ID"],
        Smartwatch_ID=alert_data.get("Smartwatch_ID"),
        Tipo_alerta=alert_data["Tipo_alerta"],
        Mensaje=alert_data["Mensaje"],
        Valor_detectado=alert_data.get("Valor_detectado"),
        Valor_umbral=alert_data.get("Valor_umbral"),
        Prioridad=alert_data.get("Prioridad", "MEDIA"),
        Timestamp_alerta=alert_data.get("Timestamp_alerta"),
        Estatus=alert_data.get("Estatus", True)
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def update_alert(db: Session, alert_id: int, alert_data: dict):
    db_alert = db.query(Alert).filter(Alert.ID == alert_id).first()
    if db_alert:
        for key, value in alert_data.items():
            setattr(db_alert, key, value)
        db.commit()
        db.refresh(db_alert)
    return db_alert

def delete_alert(db: Session, alert_id: int):
    db_alert = db.query(Alert).filter(Alert.ID == alert_id).first()
    if db_alert:
        db_alert.Estatus = False
        db.commit()
        db.refresh(db_alert)
    return db_alert