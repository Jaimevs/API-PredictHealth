from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import user_role as crud_user_role
from schemas.user_role import UserRoleCreate, UserRoleUpdate, UserRoleResponse
from typing import List

router = APIRouter(
    prefix="/user-roles",
    tags=["user-roles"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    existing_user_role = crud_user_role.get_user_role(db, user_id=user_role.Usuario_ID, role_id=user_role.Rol_ID)
    if existing_user_role:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya tiene asignado este rol"
        )
    return crud_user_role.create_user_role(db=db, user_role_data=user_role.dict())

@router.get("/user/{user_id}", response_model=List[UserRoleResponse])
def read_user_roles(user_id: int, db: Session = Depends(get_db)):
    user_roles = crud_user_role.get_user_roles(db, user_id=user_id)
    return user_roles

@router.get("/role/{role_id}", response_model=List[UserRoleResponse])
def read_role_users(role_id: int, db: Session = Depends(get_db)):
    role_users = crud_user_role.get_role_users(db, role_id=role_id)
    return role_users

@router.get("/{user_id}/{role_id}", response_model=UserRoleResponse)
def read_user_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    db_user_role = crud_user_role.get_user_role(db, user_id=user_id, role_id=role_id)
    if db_user_role is None:
        raise HTTPException(status_code=404, detail="Asignacion de rol no encontrada")
    return db_user_role

@router.put("/{user_id}/{role_id}", response_model=UserRoleResponse)
def update_user_role(user_id: int, role_id: int, user_role: UserRoleUpdate, db: Session = Depends(get_db)):
    db_user_role = crud_user_role.get_user_role(db, user_id=user_id, role_id=role_id)
    if db_user_role is None:
        raise HTTPException(status_code=404, detail="Asignacion de rol no encontrada")
    return crud_user_role.update_user_role(db=db, user_id=user_id, role_id=role_id, user_role_data=user_role.dict(exclude_unset=True))

@router.delete("/{user_id}/{role_id}", response_model=UserRoleResponse)
def delete_user_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    db_user_role = crud_user_role.get_user_role(db, user_id=user_id, role_id=role_id)
    if db_user_role is None:
        raise HTTPException(status_code=404, detail="Asignacion de rol no encontrada")
    return crud_user_role.delete_user_role(db=db, user_id=user_id, role_id=role_id)