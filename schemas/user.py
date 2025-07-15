from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    Persona_Id: int
    Nombre_Usuario: str
    Correo_Electronico: EmailStr
    Numero_Telefonico_Movil: Optional[str] = None
    Estatus: Optional[bool] = True

class UserCreate(UserBase):
    Contrasena: str

class UserUpdate(BaseModel):
    Persona_Id: Optional[int] = None
    Nombre_Usuario: Optional[str] = None
    Correo_Electronico: Optional[EmailStr] = None
    Contrasena: Optional[str] = None
    Numero_Telefonico_Movil: Optional[str] = None
    Estatus: Optional[bool] = None

class UserResponse(UserBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True