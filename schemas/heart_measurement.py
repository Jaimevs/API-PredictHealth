from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal

class HeartMeasurementBase(BaseModel):
    Usuario_ID: int
    Smartwatch_ID: int
    Timestamp_medicion: datetime
    Frecuencia_cardiaca: int
    Presion_sistolica: Optional[int] = None
    Presion_diastolica: Optional[int] = None
    Saturacion_oxigeno: Optional[Decimal] = None
    Temperatura: Optional[Decimal] = None
    Nivel_estres: Optional[int] = Field(None, ge=0, le=100)
    Variabilidad_ritmo: Optional[Decimal] = None
    Estatus: Optional[bool] = True

class HeartMeasurementCreate(HeartMeasurementBase):
    pass

class HeartMeasurementUpdate(BaseModel):
    Usuario_ID: Optional[int] = None
    Smartwatch_ID: Optional[int] = None
    Timestamp_medicion: Optional[datetime] = None
    Frecuencia_cardiaca: Optional[int] = None
    Presion_sistolica: Optional[int] = None
    Presion_diastolica: Optional[int] = None
    Saturacion_oxigeno: Optional[Decimal] = None
    Temperatura: Optional[Decimal] = None
    Nivel_estres: Optional[int] = Field(None, ge=0, le=100)
    Variabilidad_ritmo: Optional[Decimal] = None
    Estatus: Optional[bool] = None

class HeartMeasurementResponse(HeartMeasurementBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True