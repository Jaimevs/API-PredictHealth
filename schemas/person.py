from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from enum import Enum

class GenderEnum(str, Enum):
    H = "H"
    M = "M"
    NB = "N/B"

class PersonBase(BaseModel):
    Nombre: str
    Primer_Apellido: str
    Segundo_Apellido: Optional[str] = None
    Fecha_Nacimiento: date
    Genero: GenderEnum
    Estatus: Optional[bool] = True

class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    Nombre: Optional[str] = None
    Primer_Apellido: Optional[str] = None
    Segundo_Apellido: Optional[str] = None
    Fecha_Nacimiento: Optional[date] = None
    Genero: Optional[GenderEnum] = None
    Estatus: Optional[bool] = None

class PersonResponse(PersonBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True