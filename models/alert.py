from sqlalchemy import Column, Integer, BigInteger, String, Text, Numeric, Enum, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
import enum

class AlertTypeEnum(enum.Enum):
    FRECUENCIA_ALTA = "FRECUENCIA_ALTA"
    FRECUENCIA_BAJA = "FRECUENCIA_BAJA"
    PRESION_ALTA = "PRESION_ALTA"
    SATURACION_BAJA = "SATURACION_BAJA"
    CAIDA_DETECTADA = "CAIDA_DETECTADA"
    MEDICAMENTO = "MEDICAMENTO"
    EJERCICIO = "EJERCICIO"
    PERSONALIZADA = "PERSONALIZADA"

class PriorityEnum(enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

class Alert(Base):
    __tablename__ = "tbb_alertas"
    
    ID = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID", ondelete="CASCADE"), nullable=False)
    Smartwatch_ID = Column(Integer, ForeignKey("tbb_smartwatches.ID", ondelete="SET NULL"), nullable=True)
    Tipo_alerta = Column(Enum(AlertTypeEnum), nullable=False)
    Mensaje = Column(Text, nullable=False)
    Valor_detectado = Column(Numeric(10, 2), nullable=True)
    Valor_umbral = Column(Numeric(10, 2), nullable=True)
    Prioridad = Column(Enum(PriorityEnum), nullable=True, default=PriorityEnum.MEDIA)
    Timestamp_alerta = Column(DateTime, nullable=False, default=func.now())
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    smartwatch = relationship("Smartwatch", back_populates="alerts")