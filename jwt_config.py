# jwt_config.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config.settings import settings

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def solicita_token(user_data: dict, roles: list = None) -> dict:
    """Genera un token de acceso completo"""
    if roles is None:
        roles = []
    
    # Crear payload con información del usuario
    token_data = {
        "sub": str(user_data.get("id")),  # Subject (ID del usuario)
        "email": user_data.get("email", ""),
        "username": user_data.get("username", ""),
        "roles": roles
    }
    
    # Generar token
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_data.get("id"),
        "username": user_data.get("username", ""),
        "email": user_data.get("email", ""),
        "roles": roles,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # en segundos
    }

def valida_token(token: str) -> dict:
    """Valida y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# Alias para compatibilidad
decode_token = valida_token