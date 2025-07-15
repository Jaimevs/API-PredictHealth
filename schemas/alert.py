from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum

class AlertTypeEnum(str, Enum):
    FRECUENCIA_ALTA = "FRECUENCIA_ALTA"
    FRECUENCIA_BAJA = "FRECUENCIA_BAJA"
    PRESION_ALTA = "PRESION_ALTA"
    SATURACION_BAJA = "SATURACION_BAJA"
    CAIDA_DETECTADA = "CAIDA_DETECTADA"
    MEDICAMENTO = "MEDICAMENTO"
    EJERCICIO = "EJERCICIO"
    PERSONALIZADA = "PERSONALIZADA"

class PriorityEnum(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

class AlertBase(BaseModel):
    Usuario_ID: int
    Smartwatch_ID: Optional[int] = None
    Tipo_alerta: AlertTypeEnum
    Mensaje: str
    Valor_detectado: Optional[Decimal] = None
    Valor_umbral: Optional[Decimal] = None
    Prioridad: Optional[PriorityEnum] = PriorityEnum.MEDIA
    Timestamp_alerta: Optional[datetime] = None
    Estatus: Optional[bool] = True

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    Usuario_ID: Optional[int] = None
    Smartwatch_ID: Optional[int] = None
    Tipo_alerta: Optional[AlertTypeEnum] = None
    Mensaje: Optional[str] = None
    Valor_detectado: Optional[Decimal] = None
    Valor_umbral: Optional[Decimal] = None
    Prioridad: Optional[PriorityEnum] = None
    Timestamp_alerta: Optional[datetime] = None
    Estatus: Optional[bool] = None

class AlertResponse(AlertBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True