from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserRoleBase(BaseModel):
    Usuario_ID: int
    Rol_ID: int
    Estatus: Optional[bool] = True

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleUpdate(BaseModel):
    Estatus: Optional[bool] = None

class UserRoleResponse(UserRoleBase):
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True