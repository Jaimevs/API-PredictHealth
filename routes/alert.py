from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import alert as crud_alert
from schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from typing import List

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    return crud_alert.create_alert(db=db, alert_data=alert.dict())

@router.get("/", response_model=List[AlertResponse])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = crud_alert.get_alerts(db, skip=skip, limit=limit)
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
def read_alert(alert_id: int, db: Session = Depends(get_db)):
    db_alert = crud_alert.get_alert(db, alert_id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return db_alert

@router.get("/user/{user_id}", response_model=List[AlertResponse])
def read_alerts_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = crud_alert.get_alerts_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return alerts

@router.get("/smartwatch/{smartwatch_id}", response_model=List[AlertResponse])
def read_alerts_by_smartwatch(smartwatch_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = crud_alert.get_alerts_by_smartwatch(db, smartwatch_id=smartwatch_id, skip=skip, limit=limit)
    return alerts

@router.get("/priority/{priority}", response_model=List[AlertResponse])
def read_alerts_by_priority(priority: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = crud_alert.get_alerts_by_priority(db, priority=priority, skip=skip, limit=limit)
    return alerts

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(alert_id: int, alert: AlertUpdate, db: Session = Depends(get_db)):
    db_alert = crud_alert.get_alert(db, alert_id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return crud_alert.update_alert(db=db, alert_id=alert_id, alert_data=alert.dict(exclude_unset=True))

@router.delete("/{alert_id}", response_model=AlertResponse)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    db_alert = crud_alert.get_alert(db, alert_id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return crud_alert.delete_alert(db=db, alert_id=alert_id)