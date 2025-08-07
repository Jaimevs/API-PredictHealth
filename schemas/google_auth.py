# schemas/google_auth.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class GoogleLoginRequest(BaseModel):
    """Esquema para login/registro con Google"""
    google_token: str
    
    @validator('google_token')
    def token_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Token de Google inválido')
        return v.strip()

class GoogleUserInfo(BaseModel):
    """Esquema para información del usuario de Google (interno)"""
    google_id: str
    email: str
    name: str

class SetPasswordRequest(BaseModel):
    """Esquema para establecer contraseña después del login con Google"""
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class GoogleAuthResponse(BaseModel):
    """Respuesta para autenticación con Google"""
    message: str
    is_new_user: bool
    user: dict
    token: dict
    needs_password: bool  # True si el usuario necesita establecer contraseña

class PasswordSetResponse(BaseModel):
    """Respuesta para establecer contraseña"""
    message: str
    can_login_with_email: bool