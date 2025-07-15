from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from config.database import Base

class Role(Base):
    __tablename__ = "tbc_roles"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Nombre = Column(String(60), nullable=False, unique=True)
    Descripcion = Column(Text, nullable=True)
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
