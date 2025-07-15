from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from crud import role as crud_role
from schemas.role import RoleCreate, RoleUpdate, RoleResponse
from typing import List

router = APIRouter(
    prefix="/roles",
    tags=["roles"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    existing_role = crud_role.get_role_by_name(db, name=role.Nombre)
    if existing_role:
        raise HTTPException(
            status_code=400,
            detail="El nombre del rol ya existe"
        )
    return crud_role.create_role(db=db, role_data=role.dict())

@router.get("/", response_model=List[RoleResponse])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = crud_role.get_roles(db, skip=skip, limit=limit)
    return roles

@router.get("/{role_id}", response_model=RoleResponse)
def read_role(role_id: int, db: Session = Depends(get_db)):
    db_role = crud_role.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return db_role

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db)):
    db_role = crud_role.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    if role.Nombre:
        existing_role = crud_role.get_role_by_name(db, name=role.Nombre)
        if existing_role and existing_role.ID != role_id:
            raise HTTPException(
                status_code=400,
                detail="El nombre del rol ya existe"
            )
    
    return crud_role.update_role(db=db, role_id=role_id, role_data=role.dict(exclude_unset=True))

@router.delete("/{role_id}", response_model=RoleResponse)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    db_role = crud_role.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return crud_role.delete_role(db=db, role_id=role_id)