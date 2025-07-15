from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import heart_measurement as crud_heart_measurement
from schemas.heart_measurement import HeartMeasurementCreate, HeartMeasurementUpdate, HeartMeasurementResponse
from typing import List

router = APIRouter(
    prefix="/heart-measurements",
    tags=["heart-measurements"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=HeartMeasurementResponse, status_code=status.HTTP_201_CREATED)
def create_heart_measurement(measurement: HeartMeasurementCreate, db: Session = Depends(get_db)):
    return crud_heart_measurement.create_heart_measurement(db=db, measurement_data=measurement.dict())

@router.get("/", response_model=List[HeartMeasurementResponse])
def read_heart_measurements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    measurements = crud_heart_measurement.get_heart_measurements(db, skip=skip, limit=limit)
    return measurements

@router.get("/{measurement_id}", response_model=HeartMeasurementResponse)
def read_heart_measurement(measurement_id: int, db: Session = Depends(get_db)):
    db_measurement = crud_heart_measurement.get_heart_measurement(db, measurement_id=measurement_id)
    if db_measurement is None:
        raise HTTPException(status_code=404, detail="Medicion cardiaca no encontrada")
    return db_measurement

@router.get("/user/{user_id}", response_model=List[HeartMeasurementResponse])
def read_heart_measurements_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    measurements = crud_heart_measurement.get_heart_measurements_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return measurements

@router.get("/smartwatch/{smartwatch_id}", response_model=List[HeartMeasurementResponse])
def read_heart_measurements_by_smartwatch(smartwatch_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    measurements = crud_heart_measurement.get_heart_measurements_by_smartwatch(db, smartwatch_id=smartwatch_id, skip=skip, limit=limit)
    return measurements

@router.put("/{measurement_id}", response_model=HeartMeasurementResponse)
def update_heart_measurement(measurement_id: int, measurement: HeartMeasurementUpdate, db: Session = Depends(get_db)):
    db_measurement = crud_heart_measurement.get_heart_measurement(db, measurement_id=measurement_id)
    if db_measurement is None:
        raise HTTPException(status_code=404, detail="Medicion cardiaca no encontrada")
    return crud_heart_measurement.update_heart_measurement(db=db, measurement_id=measurement_id, measurement_data=measurement.dict(exclude_unset=True))

@router.delete("/{measurement_id}", response_model=HeartMeasurementResponse)
def delete_heart_measurement(measurement_id: int, db: Session = Depends(get_db)):
    db_measurement = crud_heart_measurement.get_heart_measurement(db, measurement_id=measurement_id)
    if db_measurement is None:
        raise HTTPException(status_code=404, detail="Medicion cardiaca no encontrada")
    return crud_heart_measurement.delete_heart_measurement(db=db, measurement_id=measurement_id)