from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

class BloodTypeEnum(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class HealthProfileBase(BaseModel):
    Usuario_ID: int
    Peso_kg: Optional[Decimal] = None
    Altura_cm: Optional[Decimal] = None
    Tipo_sangre: Optional[BloodTypeEnum] = None
    Fumador: Optional[bool] = False
    Diabetico: Optional[bool] = False
    Hipertenso: Optional[bool] = False
    Historial_cardiaco: Optional[bool] = False
    Estatus: Optional[bool] = True

class HealthProfileCreate(HealthProfileBase):
    pass

class HealthProfileUpdate(BaseModel):
    Peso_kg: Optional[Decimal] = None
    Altura_cm: Optional[Decimal] = None
    Tipo_sangre: Optional[BloodTypeEnum] = None
    Fumador: Optional[bool] = None
    Diabetico: Optional[bool] = None
    Hipertenso: Optional[bool] = None
    Historial_cardiaco: Optional[bool] = None
    Estatus: Optional[bool] = None

class HealthProfileResponse(HealthProfileBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True