from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import smartwatch as crud_smartwatch
from schemas.smartwatch import SmartwatchCreate, SmartwatchUpdate, SmartwatchResponse
from typing import List

router = APIRouter(
    prefix="/smartwatches",
    tags=["smartwatches"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=SmartwatchResponse, status_code=status.HTTP_201_CREATED)
def create_smartwatch(smartwatch: SmartwatchCreate, db: Session = Depends(get_db)):
    existing_smartwatch = crud_smartwatch.get_smartwatch_by_serial(db, serial=smartwatch.Numero_serie)
    if existing_smartwatch:
        raise HTTPException(
            status_code=400,
            detail="El n�mero de serie ya esta registrado"
        )
    return crud_smartwatch.create_smartwatch(db=db, smartwatch_data=smartwatch.dict())

@router.get("/", response_model=List[SmartwatchResponse])
def read_smartwatches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    smartwatches = crud_smartwatch.get_smartwatches(db, skip=skip, limit=limit)
    return smartwatches

@router.get("/{smartwatch_id}", response_model=SmartwatchResponse)
def read_smartwatch(smartwatch_id: int, db: Session = Depends(get_db)):
    db_smartwatch = crud_smartwatch.get_smartwatch(db, smartwatch_id=smartwatch_id)
    if db_smartwatch is None:
        raise HTTPException(status_code=404, detail="Smartwatch no encontrado")
    return db_smartwatch

@router.get("/user/{user_id}", response_model=List[SmartwatchResponse])
def read_smartwatches_by_user(user_id: int, db: Session = Depends(get_db)):
    smartwatches = crud_smartwatch.get_smartwatches_by_user(db, user_id=user_id)
    return smartwatches

@router.put("/{smartwatch_id}", response_model=SmartwatchResponse)
def update_smartwatch(smartwatch_id: int, smartwatch: SmartwatchUpdate, db: Session = Depends(get_db)):
    db_smartwatch = crud_smartwatch.get_smartwatch(db, smartwatch_id=smartwatch_id)
    if db_smartwatch is None:
        raise HTTPException(status_code=404, detail="Smartwatch no encontrado")
    
    if smartwatch.Numero_serie:
        existing_smartwatch = crud_smartwatch.get_smartwatch_by_serial(db, serial=smartwatch.Numero_serie)
        if existing_smartwatch and existing_smartwatch.ID != smartwatch_id:
            raise HTTPException(
                status_code=400,
                detail="El nomero de serie ya esta registrado"
            )
    
    return crud_smartwatch.update_smartwatch(db=db, smartwatch_id=smartwatch_id, smartwatch_data=smartwatch.dict(exclude_unset=True))

@router.delete("/{smartwatch_id}", response_model=SmartwatchResponse)
def delete_smartwatch(smartwatch_id: int, db: Session = Depends(get_db)):
    db_smartwatch = crud_smartwatch.get_smartwatch(db, smartwatch_id=smartwatch_id)
    if db_smartwatch is None:
        raise HTTPException(status_code=404, detail="Smartwatch no encontrado")
    return crud_smartwatch.delete_smartwatch(db=db, smartwatch_id=smartwatch_id)