from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import person as crud_person
from schemas.person import PersonCreate, PersonUpdate, PersonResponse
from typing import List

router = APIRouter(
    prefix="/persons",
    tags=["persons"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    return crud_person.create_person(db=db, person_data=person.dict())

@router.get("/", response_model=List[PersonResponse])
def read_persons(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    persons = crud_person.get_persons(db, skip=skip, limit=limit)
    return persons

@router.get("/{person_id}", response_model=PersonResponse)
def read_person(person_id: int, db: Session = Depends(get_db)):
    db_person = crud_person.get_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return db_person

@router.put("/{person_id}", response_model=PersonResponse)
def update_person(person_id: int, person: PersonUpdate, db: Session = Depends(get_db)):
    db_person = crud_person.get_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return crud_person.update_person(db=db, person_id=person_id, person_data=person.dict(exclude_unset=True))

@router.delete("/{person_id}", response_model=PersonResponse)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = crud_person.get_person(db, person_id=person_id)
    if db_person is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return crud_person.delete_person(db=db, person_id=person_id)