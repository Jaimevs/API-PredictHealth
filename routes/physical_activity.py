from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import physical_activity as crud_physical_activity
from schemas.physical_activity import PhysicalActivityCreate, PhysicalActivityUpdate, PhysicalActivityResponse
from typing import List

router = APIRouter(
    prefix="/physical-activities",
    tags=["physical-activities"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=PhysicalActivityResponse, status_code=status.HTTP_201_CREATED)
def create_physical_activity(activity: PhysicalActivityCreate, db: Session = Depends(get_db)):
    return crud_physical_activity.create_physical_activity(db=db, activity_data=activity.dict())

@router.get("/", response_model=List[PhysicalActivityResponse])
def read_physical_activities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activities = crud_physical_activity.get_physical_activities(db, skip=skip, limit=limit)
    return activities

@router.get("/{activity_id}", response_model=PhysicalActivityResponse)
def read_physical_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = crud_physical_activity.get_physical_activity(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Actividad fisica no encontrada")
    return db_activity

@router.get("/user/{user_id}", response_model=List[PhysicalActivityResponse])
def read_physical_activities_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activities = crud_physical_activity.get_physical_activities_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return activities

@router.get("/smartwatch/{smartwatch_id}", response_model=List[PhysicalActivityResponse])
def read_physical_activities_by_smartwatch(smartwatch_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    activities = crud_physical_activity.get_physical_activities_by_smartwatch(db, smartwatch_id=smartwatch_id, skip=skip, limit=limit)
    return activities

@router.put("/{activity_id}", response_model=PhysicalActivityResponse)
def update_physical_activity(activity_id: int, activity: PhysicalActivityUpdate, db: Session = Depends(get_db)):
    db_activity = crud_physical_activity.get_physical_activity(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Actividad fisica no encontrada")
    return crud_physical_activity.update_physical_activity(db=db, activity_id=activity_id, activity_data=activity.dict(exclude_unset=True))

@router.delete("/{activity_id}", response_model=PhysicalActivityResponse)
def delete_physical_activity(activity_id: int, db: Session = Depends(get_db)):
    db_activity = crud_physical_activity.get_physical_activity(db, activity_id=activity_id)
    if db_activity is None:
        raise HTTPException(status_code=404, detail="Actividad fisica no encontrada")
    return crud_physical_activity.delete_physical_activity(db=db, activity_id=activity_id)