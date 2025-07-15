from sqlalchemy import Column, Integer, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class UserRole(Base):
    __tablename__ = "tbd_usuarios_roles"
    
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID", ondelete="CASCADE"), primary_key=True)
    Rol_ID = Column(Integer, ForeignKey("tbc_roles.ID", ondelete="CASCADE"), primary_key=True)
    Estatus = Column(Boolean, nullable=False, default=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
