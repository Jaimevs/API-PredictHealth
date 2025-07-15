from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import health_profile as crud_health_profile
from schemas.health_profile import HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse
from typing import List

router = APIRouter(
    prefix="/health-profiles",
    tags=["health-profiles"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=HealthProfileResponse, status_code=status.HTTP_201_CREATED)
def create_health_profile(profile: HealthProfileCreate, db: Session = Depends(get_db)):
    existing_profile = crud_health_profile.get_health_profile_by_user(db, user_id=profile.Usuario_ID)
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya tiene un perfil de salud"
        )
    return crud_health_profile.create_health_profile(db=db, profile_data=profile.dict())

@router.get("/", response_model=List[HealthProfileResponse])
def read_health_profiles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    profiles = crud_health_profile.get_health_profiles(db, skip=skip, limit=limit)
    return profiles

@router.get("/{profile_id}", response_model=HealthProfileResponse)
def read_health_profile(profile_id: int, db: Session = Depends(get_db)):
    db_profile = crud_health_profile.get_health_profile(db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Perfil de salud no encontrado")
    return db_profile

@router.get("/user/{user_id}", response_model=HealthProfileResponse)
def read_health_profile_by_user(user_id: int, db: Session = Depends(get_db)):
    db_profile = crud_health_profile.get_health_profile_by_user(db, user_id=user_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Perfil de salud no encontrado")
    return db_profile

@router.put("/{profile_id}", response_model=HealthProfileResponse)
def update_health_profile(profile_id: int, profile: HealthProfileUpdate, db: Session = Depends(get_db)):
    db_profile = crud_health_profile.get_health_profile(db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Perfil de salud no encontrado")
    return crud_health_profile.update_health_profile(db=db, profile_id=profile_id, profile_data=profile.dict(exclude_unset=True))

@router.delete("/{profile_id}", response_model=HealthProfileResponse)
def delete_health_profile(profile_id: int, db: Session = Depends(get_db)):
    db_profile = crud_health_profile.get_health_profile(db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Perfil de salud no encontrado")
    return crud_health_profile.delete_health_profile(db=db, profile_id=profile_id)