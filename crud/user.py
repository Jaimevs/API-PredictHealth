from sqlalchemy.orm import Session
from models.user import User
from models.user_role import UserRole
from models.role import Role
from typing import Optional, List
import crud.person as person_crud

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Obtiene un usuario por ID"""
    return db.query(User).filter(User.ID == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Obtiene un usuario por correo electrónico"""
    return db.query(User).filter(User.Correo_Electronico == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Obtiene un usuario por nombre de usuario"""
    return db.query(User).filter(User.Nombre_Usuario == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de usuarios"""
    return db.query(User).filter(User.Estatus == True).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: dict) -> User:
    """
    Crea un nuevo usuario con persona vacía automática
    Solo se almacenan datos básicos del usuario
    """
    # Crear persona vacía primero (automáticamente)
    db_person = person_crud.create_empty_person(db)
    persona_id = db_person.ID
    
    # Crear usuario con datos básicos únicamente
    db_user = User(
        Persona_Id=persona_id,
        Nombre_Usuario=user_data["nombre_usuario"],
        Correo_Electronico=user_data["correo_electronico"],
        Contrasena=user_data["contrasena_hash"],  # Ya viene hasheada
        Numero_Telefonico_Movil=user_data.get("numero_telefonico_movil"),
        Estatus=user_data.get("estatus", True)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Asignar rol de USUARIO por defecto (ID=2)
    assign_default_role(db, db_user.ID)
    
    return db_user

def assign_default_role(db: Session, user_id: int, role_id: int = 2):
    """Asigna el rol por defecto al usuario (USUARIO = ID 2)"""
    user_role = UserRole(
        Usuario_ID=user_id,
        Rol_ID=role_id,
        Estatus=True
    )
    db.add(user_role)
    db.commit()

def get_user_roles(db: Session, user_id: int) -> List[Role]:
    """Obtiene los roles de un usuario"""
    return db.query(Role).join(UserRole).filter(
        UserRole.Usuario_ID == user_id,
        UserRole.Estatus == True,
        Role.Estatus == True
    ).all()

def update_user(db: Session, user_id: int, user_update: dict) -> Optional[User]:
    """Actualiza un usuario existente"""
    db_user = db.query(User).filter(User.ID == user_id).first()
    if db_user:
        for field, value in user_update.items():
            if hasattr(db_user, field) and value is not None:
                setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Desactiva un usuario (soft delete)"""
    db_user = db.query(User).filter(User.ID == user_id).first()
    if db_user:
        db_user.Estatus = False
        db.commit()
        return True
    return False

def activate_user(db: Session, user_id: int) -> Optional[User]:
    """Activa un usuario"""
    return update_user(db, user_id, {"Estatus": True})

def deactivate_user(db: Session, user_id: int) -> Optional[User]:
    """Desactiva un usuario"""
    return update_user(db, user_id, {"Estatus": False})

def authenticate_user(db: Session, username: str, password: str, pwd_context) -> Optional[User]:
    """Autentica un usuario por username/email y contraseña"""
    # Buscar por nombre de usuario
    user = get_user_by_username(db, username)
    if not user:
        # Si no encuentra por username, buscar por email
        user = get_user_by_email(db, username)
    
    if not user:
        return None
    
    # Verificar contraseña
    if not pwd_context.verify(password, user.Contrasena):
        return None
    
    # Verificar que el usuario esté activo
    if not user.Estatus:
        return None
    
    return user