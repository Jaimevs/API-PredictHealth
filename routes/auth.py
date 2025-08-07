# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from config.database import get_db
from schemas.auth import (
    UserRegister, EmailVerification, UserLogin, 
    RegistrationResponse, VerificationResponse, Token
)
from email_service import send_verification_email, generate_verification_code
from token_verification import (
    store_pending_registration, verify_code_only, 
    get_pending_registration, remove_pending_registration
)
from jwt_config import solicita_token
from dependencies.auth import get_current_user, get_current_active_user, require_admin
import crud.user as user_crud

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

# Configuración para hash de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera hash de la contraseña"""
    return pwd_context.hash(password)

@router.post("/register", response_model=RegistrationResponse)
async def register_user(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario y envía código de verificación por email
    El persona_id se asigna automáticamente
    """
    # Verificar si el usuario ya existe
    if user_crud.get_user_by_email(db, email=user_data.correo_electronico):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
    
    if user_crud.get_user_by_username(db, username=user_data.nombre_usuario):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    # Generar código de verificación
    verification_code = generate_verification_code()
    
    # Preparar datos del usuario para almacenamiento temporal
    user_dict = {
        "correo_electronico": user_data.correo_electronico,
        "nombre_usuario": user_data.nombre_usuario,
        "contrasena_hash": get_password_hash(user_data.contrasena),
        "numero_telefonico_movil": user_data.numero_telefonico_movil,
        "estatus": True
        # NO se incluyen datos de persona - se crea vacía automáticamente
    }
    
    # Almacenar registro pendiente
    token = store_pending_registration(user_dict, verification_code)
    
    # Enviar email de verificación en segundo plano
    background_tasks.add_task(
        send_verification_email, 
        user_data.correo_electronico, 
        verification_code
    )
    
    return RegistrationResponse(
        message="Se ha enviado un código de verificación a tu correo electrónico",
        email=user_data.correo_electronico,
        verification_required=True
    )

@router.post("/verify-email", response_model=VerificationResponse)
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db)
):
    """
    Verifica el código de email y crea el usuario en la base de datos
    Solo necesita el código de verificación
    """
    # Verificar código (busca en todos los registros pendientes)
    token = verify_code_only(verification_data.verification_code)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de verificación inválido o expirado"
        )
    
    # Obtener datos del registro pendiente
    user_data = get_pending_registration(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registro no encontrado o expirado"
        )
    
    # Crear usuario en la base de datos (automáticamente crea la persona vacía)
    try:
        db_user = user_crud.create_user(db=db, user_data=user_data)
        
        # Obtener roles del usuario (automáticamente se asigna USUARIO)
        user_roles = user_crud.get_user_roles(db, user_id=db_user.ID)
        role_names = [role.Nombre for role in user_roles] if user_roles else ["USUARIO"]
        
        # Generar token JWT
        token_data = solicita_token(
            user_data={
                "id": db_user.ID,
                "email": db_user.Correo_Electronico,
                "username": db_user.Nombre_Usuario
            },
            roles=role_names
        )
        
        # Eliminar registro pendiente
        remove_pending_registration(token)
        
        return VerificationResponse(
            message="Código verificado exitosamente. Usuario creado con persona vacía.",
            user=db_user,
            token=Token(**token_data)
        )
        
    except Exception as e:
        # Si hay error al crear usuario, mantener el registro pendiente
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario con email y contraseña
    """
    user = user_crud.authenticate_user(
        db, 
        user_credentials.email,  # Solo email
        user_credentials.password, 
        pwd_context
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.Estatus:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Obtener roles del usuario
    user_roles = user_crud.get_user_roles(db, user_id=user.ID)
    role_names = [role.Nombre for role in user_roles] if user_roles else ["USUARIO"]
    
    # Generar token
    token_data = solicita_token(
        user_data={
            "id": user.ID,
            "email": user.Correo_Electronico,
            "username": user.Nombre_Usuario
        },
        roles=role_names
    )
    
    return Token(**token_data)

@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """
    Obtiene información del usuario actual
    """
    return {
        "ID": current_user.ID,
        "Nombre_Usuario": current_user.Nombre_Usuario,
        "Correo_Electronico": current_user.Correo_Electronico,
        "Numero_Telefonico_Movil": current_user.Numero_Telefonico_Movil,
        "Estatus": current_user.Estatus,
        "Fecha_Registro": current_user.Fecha_Registro,
        "Persona_Id": current_user.Persona_Id
    }

@router.post("/resend-verification")
async def resend_verification_code(
    email: str,
    background_tasks: BackgroundTasks
):
    """
    Reenvía el código de verificación a un email
    """
    verification_code = generate_verification_code()
    
    background_tasks.add_task(
        send_verification_email,
        email,
        verification_code
    )
    
    return {"message": "Código de verificación reenviado"}

@router.post("/logout")
async def logout(current_user = Depends(get_current_active_user)):
    """
    Cierra sesión del usuario
    """
    return {"message": "Sesión cerrada exitosamente"}

# Endpoints administrativos
@router.get("/users", dependencies=[Depends(require_admin())])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los usuarios (solo ADMIN)
    """
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}/deactivate", dependencies=[Depends(require_admin())])
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Desactiva un usuario (solo ADMIN)
    """
    user = user_crud.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return {"message": "Usuario desactivado exitosamente"}