from sqlalchemy import Column, Integer, Numeric, Enum, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base
import enum

class BloodTypeEnum(enum.Enum):
    A_PLUS = "A+"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B_MINUS = "B-"
    AB_PLUS = "AB+"
    AB_MINUS = "AB-"
    O_PLUS = "O+"
    O_MINUS = "O-"

class HealthProfile(Base):
    __tablename__ = "tbb_perfil_salud"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID", ondelete="CASCADE"), nullable=False, unique=True)
    Peso_kg = Column(Numeric(5, 2), nullable=True)
    Altura_cm = Column(Numeric(5, 2), nullable=True)
    Tipo_sangre = Column(Enum(BloodTypeEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    Fumador = Column(Boolean, nullable=True, default=False)
    Diabetico = Column(Boolean, nullable=True, default=False)
    Hipertenso = Column(Boolean, nullable=True, default=False)
    Historial_cardiaco = Column(Boolean, nullable=True, default=False)
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="health_profile")