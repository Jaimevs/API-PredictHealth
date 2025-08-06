from sqlalchemy import Column, Integer, String, Date, Enum, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from config.database import Base
import enum

class GenderEnum(enum.Enum):
    H = "H"
    M = "M"
    NB = "N/B"

class Person(Base):
    __tablename__ = "tbb_personas"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
   
    Nombre = Column(String(80), nullable=True)  
    Primer_Apellido = Column(String(80), nullable=True)  
    Segundo_Apellido = Column(String(80), nullable=True)  
    Fecha_Nacimiento = Column(Date, nullable=True)  
    Genero = Column(Enum(GenderEnum), nullable=True)  
    
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="person", cascade="all, delete-orphan")