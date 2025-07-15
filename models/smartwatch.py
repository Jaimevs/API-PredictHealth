from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class Smartwatch(Base):
    __tablename__ = "tbb_smartwatches"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID", ondelete="CASCADE"), nullable=False)
    Marca = Column(String(50), nullable=False)
    Modelo = Column(String(100), nullable=False)
    Numero_serie = Column(String(100), nullable=False, unique=True)
    Fecha_vinculacion = Column(DateTime, nullable=False, default=func.now())
    Activo = Column(Boolean, nullable=True, default=True)
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="smartwatches")
    heart_measurements = relationship("HeartMeasurement", back_populates="smartwatch", cascade="all, delete-orphan")
    physical_activities = relationship("PhysicalActivity", back_populates="smartwatch", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="smartwatch", cascade="all, delete-orphan")
