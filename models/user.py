from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
from config.database import Base

class User(Base):
    __tablename__ = "tbb_usuarios"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Persona_Id = Column(Integer, ForeignKey("tbb_personas.ID", ondelete="CASCADE"), nullable=False)
    Nombre_Usuario = Column(String(100), nullable=False, unique=True)
    Correo_Electronico = Column(String(100), nullable=False, unique=True)
    Contrasena = Column(String(255), nullable=False)
    Numero_Telefonico_Movil = Column(String(20), nullable=True)
    Estatus = Column(Boolean, nullable=False, default=True)

    Google_ID = Column(String(100), nullable=True, unique=True)

    Fecha_Registro = Column(DateTime, nullable=False, default=func.now())
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=func.now())
    
    # Relationships
    person = relationship("Person", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    smartwatches = relationship("Smartwatch", back_populates="user", cascade="all, delete-orphan")
    heart_measurements = relationship("HeartMeasurement", back_populates="user", cascade="all, delete-orphan")
    physical_activities = relationship("PhysicalActivity", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
