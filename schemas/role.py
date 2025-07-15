from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RoleBase(BaseModel):
    Nombre: str
    Descripcion: Optional[str] = None
    Estatus: Optional[bool] = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    Nombre: Optional[str] = None
    Descripcion: Optional[str] = None
    Estatus: Optional[bool] = None

class RoleResponse(RoleBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True