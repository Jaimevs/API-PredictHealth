from sqlalchemy import Column, Integer, BigInteger, Numeric, DateTime, func, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from config.database import Base

class HeartMeasurement(Base):
    __tablename__ = "tbb_mediciones_cardiacas"
    
    ID = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID", ondelete="CASCADE"), nullable=False)
    Smartwatch_ID = Column(Integer, ForeignKey("tbb_smartwatches.ID", ondelete="CASCADE"), nullable=False)
    Timestamp_medicion = Column(DateTime, nullable=False)
    Frecuencia_cardiaca = Column(Integer, nullable=False)
    Presion_sistolica = Column(Integer, nullable=True)
    Presion_diastolica = Column(Integer, nullable=True)
    Saturacion_oxigeno = Column(Numeric(4, 1), nullable=True)
    Temperatura = Column(Numeric(3, 1), nullable=True)
    Nivel_estres = Column(Integer, nullable=True)
    Variabilidad_ritmo = Column(Numeric(5, 2), nullable=True)
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('Nivel_estres >= 0 AND Nivel_estres <= 100', name='check_nivel_estres'),
    )
    
    # Relationships
    user = relationship("User", back_populates="heart_measurements")
    smartwatch = relationship("Smartwatch", back_populates="heart_measurements")