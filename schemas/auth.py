# schemas/auth.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    """Esquema para registro de usuario - Solo datos básicos"""
    correo_electronico: EmailStr
    nombre_usuario: str
    contrasena: str
    numero_telefonico_movil: Optional[str] = None
    
    @validator('nombre_usuario')
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')
        if len(v) > 100:
            raise ValueError('El nombre de usuario debe tener máximo 100 caracteres')
        return v
    
    @validator('contrasena')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class EmailVerification(BaseModel):
    """Esquema para verificación de email - Solo código"""
    verification_code: str
    
    @validator('verification_code')
    def code_must_be_valid(cls, v):
        if len(v) != 6:
            raise ValueError('El código de verificación debe tener 6 dígitos')
        if not v.isdigit():
            raise ValueError('El código de verificación solo debe contener números')
        return v

class UserLogin(BaseModel):
    """Esquema para login de usuario"""
    username: str  # Puede ser nombre_usuario o correo_electronico
    password: str

class Token(BaseModel):
    """Esquema para respuesta de token"""
    access_token: str
    token_type: str
    user_id: int
    username: str
    email: str
    roles: List[str]
    expires_in: int

class TokenData(BaseModel):
    """Esquema para datos del token"""
    sub: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    roles: List[str] = []

class UserResponse(BaseModel):
    """Esquema para respuesta de usuario"""
    ID: int
    Nombre_Usuario: str
    Correo_Electronico: str
    Numero_Telefonico_Movil: Optional[str] = None
    Estatus: bool
    Fecha_Registro: datetime
    Persona_Id: int
    
    class Config:
        from_attributes = True

class RegistrationResponse(BaseModel):
    """Esquema para respuesta de registro"""
    message: str
    email: str
    verification_required: bool = True

class VerificationResponse(BaseModel):
    """Esquema para respuesta de verificación"""
    message: str
    user: UserResponse
    token: Token