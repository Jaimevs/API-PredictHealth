from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SmartwatchBase(BaseModel):
    Usuario_ID: int
    Marca: str
    Modelo: str
    Numero_serie: str
    Fecha_vinculacion: Optional[datetime] = None
    Activo: Optional[bool] = True
    Estatus: Optional[bool] = True

class SmartwatchCreate(SmartwatchBase):
    pass

class SmartwatchUpdate(BaseModel):
    Usuario_ID: Optional[int] = None
    Marca: Optional[str] = None
    Modelo: Optional[str] = None
    Numero_serie: Optional[str] = None
    Fecha_vinculacion: Optional[datetime] = None
    Activo: Optional[bool] = None
    Estatus: Optional[bool] = None

class SmartwatchResponse(SmartwatchBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True