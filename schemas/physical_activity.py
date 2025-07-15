from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class PhysicalActivityBase(BaseModel):
    Usuario_ID: int
    Smartwatch_ID: int
    Pasos: Optional[int] = None
    Distancia_km: Optional[Decimal] = None
    Calorias_quemadas: Optional[int] = None
    Minutos_actividad: Optional[int] = None
    Pisos_subidos: Optional[int] = None
    Estatus: Optional[bool] = True

class PhysicalActivityCreate(PhysicalActivityBase):
    pass

class PhysicalActivityUpdate(BaseModel):
    Usuario_ID: Optional[int] = None
    Smartwatch_ID: Optional[int] = None
    Pasos: Optional[int] = None
    Distancia_km: Optional[Decimal] = None
    Calorias_quemadas: Optional[int] = None
    Minutos_actividad: Optional[int] = None
    Pisos_subidos: Optional[int] = None
    Estatus: Optional[bool] = None

class PhysicalActivityResponse(PhysicalActivityBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True