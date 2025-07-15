from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import user as crud_user
from schemas.user import UserCreate, UserUpdate, UserResponse
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db, email=user.Correo_Electronico)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El correo electronico ya esta registrado"
        )
    
    db_user = crud_user.get_user_by_username(db, username=user.Nombre_Usuario)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya esta registrado"
        )
    
    return crud_user.create_user(db=db, user_data=user.dict())

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user.Correo_Electronico:
        existing_user = crud_user.get_user_by_email(db, email=user.Correo_Electronico)
        if existing_user and existing_user.ID != user_id:
            raise HTTPException(
                status_code=400,
                detail="El correo electronico ya esta registrado"
            )
    
    if user.Nombre_Usuario:
        existing_user = crud_user.get_user_by_username(db, username=user.Nombre_Usuario)
        if existing_user and existing_user.ID != user_id:
            raise HTTPException(
                status_code=400,
                detail="El nombre de usuario ya esta registrado"
            )
    
    return crud_user.update_user(db=db, user_id=user_id, user_data=user.dict(exclude_unset=True))

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return crud_user.delete_user(db=db, user_id=user_id)