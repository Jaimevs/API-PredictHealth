# dependencies/auth.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from config.database import get_db
from jwt_config import valida_token
from schemas.auth import TokenData
import crud.user as user_crud

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependencia para obtener el usuario actual basado en el token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Validar token
        payload = valida_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # Extraer información del token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(
            sub=user_id,
            email=payload.get("email"),
            username=payload.get("username"),
            roles=payload.get("roles", [])
        )
        
    except JWTError:
        raise credentials_exception
    
    # Buscar usuario en la base de datos
    user = user_crud.get_user(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Dependencia para obtener el usuario actual activo
    """
    if not current_user.Estatus:  # Usando tu campo Estatus
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo"
        )
    return current_user

def require_roles(required_roles: list):
    """
    Dependencia para requerir roles específicos
    Acepta nombres de roles como ["ADMIN", "MEDICO"] o IDs como [1, 3]
    """
    def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        # Validar token
        payload = valida_token(credentials.credentials)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user_roles = payload.get("roles", [])
        
        # Verificar si el usuario tiene al menos uno de los roles requeridos
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los siguientes roles: {', '.join(map(str, required_roles))}"
            )
        
        return payload
    
    return role_checker

def require_admin():
    """Dependencia específica para requerir rol de ADMIN"""
    return require_roles(["ADMIN"])

def require_medico():
    """Dependencia específica para requerir rol de MEDICO"""
    return require_roles(["MEDICO"])

def require_medico_or_admin():
    """Dependencia para requerir rol de MEDICO o ADMIN"""
    return require_roles(["MEDICO", "ADMIN"])