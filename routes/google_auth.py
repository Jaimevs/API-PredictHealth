from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from config.database import get_db
from schemas.google_auth import (
    GoogleLoginRequest, GoogleAuthResponse, 
    SetPasswordRequest, PasswordSetResponse
)
from schemas.auth import Token
from services.google_auth_service import verify_google_token
from dependencies.auth import get_current_active_user
from jwt_config import solicita_token
import crud.google_user as google_user_crud
import crud.user as user_crud

router = APIRouter(
    prefix="/google-auth",
    tags=["google_authentication"],
    responses={404: {"description": "Not found"}},
)

# Configuración para hash de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login", response_model=GoogleAuthResponse)
async def google_login(
    google_data: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login/Registro con Google
    Si el usuario no existe, se crea automáticamente
    """
    # Verificar token de Google
    google_user_info = await verify_google_token(google_data.google_token)
    
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de Google inválido"
        )
    
    # Buscar usuario existente por Google ID
    existing_user = google_user_crud.get_user_by_google_id(db, google_user_info.google_id)
    is_new_user = False
    
    if not existing_user:
        # Verificar si ya existe un usuario con ese email (registro normal)
        existing_email_user = user_crud.get_user_by_email(db, google_user_info.email)
        
        if existing_email_user:
            # Usuario ya existe con email normal, vincular con Google
            existing_email_user.Google_ID = google_user_info.google_id
            db.commit()
            db.refresh(existing_email_user)
            user = existing_email_user
        else:
            # Crear nuevo usuario de Google
            user = google_user_crud.create_google_user(
                db, 
                google_user_info.google_id,
                google_user_info.email,
                google_user_info.name
            )
            is_new_user = True
    else:
        user = existing_user
    
    # Verificar si el usuario está activo
    if not user.Estatus:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Obtener roles del usuario
    user_roles = google_user_crud.get_user_roles(db, user_id=user.ID)
    role_names = [role.Nombre for role in user_roles] if user_roles else ["USUARIO"]
    
    # Generar token JWT
    token_data = solicita_token(
        user_data={
            "id": user.ID,
            "email": user.Correo_Electronico,
            "username": user.Nombre_Usuario
        },
        roles=role_names
    )
    
    # Verificar si necesita establecer contraseña
    needs_password = not google_user_crud.user_has_password(db, user.ID)
    
    return GoogleAuthResponse(
        message="Login con Google exitoso" if not is_new_user else "Cuenta creada con Google exitosamente",
        is_new_user=is_new_user,
        user={
            "ID": user.ID,
            "Nombre_Usuario": user.Nombre_Usuario,
            "Correo_Electronico": user.Correo_Electronico,
            "Numero_Telefonico_Movil": user.Numero_Telefonico_Movil,
            "Estatus": user.Estatus,
            "Fecha_Registro": user.Fecha_Registro,
            "Persona_Id": user.Persona_Id,
            "Google_ID": user.Google_ID
        },
        token=Token(**token_data),
        needs_password=needs_password
    )

@router.post("/set-password", response_model=PasswordSetResponse)
async def set_password(
    password_data: SetPasswordRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Permite a un usuario de Google establecer una contraseña
    para poder hacer login con email/password
    """
    # Verificar que el usuario se registró con Google
    if not current_user.Google_ID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta función solo está disponible para usuarios de Google"
        )
    
    # Verificar si ya tiene contraseña
    if google_user_crud.user_has_password(db, current_user.ID):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes una contraseña establecida"
        )
    
    # Hashear la nueva contraseña
    hashed_password = pwd_context.hash(password_data.new_password)
    
    # Establecer la contraseña
    updated_user = google_user_crud.set_user_password(
        db, 
        current_user.ID, 
        hashed_password
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al establecer la contraseña"
        )
    
    return PasswordSetResponse(
        message="Contraseña establecida exitosamente. Ahora puedes hacer login con email y contraseña.",
        can_login_with_email=True
    )

@router.get("/me")
async def get_google_user_info(
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene información del usuario actual (específicamente para usuarios de Google)
    """
    return {
        "ID": current_user.ID,
        "Nombre_Usuario": current_user.Nombre_Usuario,
        "Correo_Electronico": current_user.Correo_Electronico,
        "Numero_Telefonico_Movil": current_user.Numero_Telefonico_Movil,
        "Estatus": current_user.Estatus,
        "Fecha_Registro": current_user.Fecha_Registro,
        "Persona_Id": current_user.Persona_Id,
        "Google_ID": current_user.Google_ID,
        "has_password": google_user_crud.user_has_password(get_db().__next__(), current_user.ID)
    }

@router.get("/check-password")
async def check_has_password(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verifica si el usuario actual tiene contraseña establecida
    """
    has_password = google_user_crud.user_has_password(db, current_user.ID)
    
    return {
        "has_password": has_password,
        "can_login_with_email": has_password,
        "message": "Puedes hacer login con email/contraseña" if has_password else "Necesitas establecer una contraseña"
    }