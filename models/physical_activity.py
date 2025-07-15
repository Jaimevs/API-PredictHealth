from sqlalchemy import Column, Integer, BigInteger, Numeric, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class PhysicalActivity(Base):
    __tablename__ = "tbb_actividad_fisica"
    
    ID = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID", ondelete="CASCADE"), nullable=False)
    Smartwatch_ID = Column(Integer, ForeignKey("tbb_smartwatches.ID", ondelete="CASCADE"), nullable=False)
    Pasos = Column(Integer, nullable=True)
    Distancia_km = Column(Numeric(6, 2), nullable=True)
    Calorias_quemadas = Column(Integer, nullable=True)
    Minutos_actividad = Column(Integer, nullable=True)
    Pisos_subidos = Column(Integer, nullable=True)
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="physical_activities")
    smartwatch = relationship("Smartwatch", back_populates="physical_activities")