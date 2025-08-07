from sqlalchemy.orm import Session
from models.user import User
from models.user_role import UserRole
from models.role import Role
from typing import Optional, List
import crud.person as person_crud
import crud.user as user_crud
from services.google_auth_service import generate_username_from_email

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Obtiene un usuario por su Google ID"""
    return db.query(User).filter(User.Google_ID == google_id).first()

def create_google_user(db: Session, google_id: str, email: str, name: str) -> User:
    """
    Crea un nuevo usuario con autenticación de Google
    """
    # Crear persona vacía primero
    db_person = person_crud.create_empty_person(db)
    persona_id = db_person.ID
    
    # Generar nombre de usuario único
    base_username = generate_username_from_email(email)
    username = base_username
    counter = 1
    
    # Verificar que el username sea único
    while user_crud.get_user_by_username(db, username):
        username = f"{base_username}_{counter}"
        counter += 1
    
    # Crear usuario de Google
    db_user = User(
        Persona_Id=persona_id,
        Nombre_Usuario=username,
        Correo_Electronico=email,
        Contrasena=None,  # Sin contraseña inicialmente
        Google_ID=google_id,
        Numero_Telefonico_Movil=None,
        Estatus=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Asignar rol de USUARIO por defecto (ID=2)
    user_role = UserRole(
        Usuario_ID=db_user.ID,
        Rol_ID=2,  # USUARIO
        Estatus=True
    )
    db.add(user_role)
    db.commit()
    
    return db_user

def set_user_password(db: Session, user_id: int, hashed_password: str) -> Optional[User]:
    """
    Establece una contraseña para un usuario de Google
    """
    db_user = db.query(User).filter(User.ID == user_id).first()
    if db_user:
        db_user.Contrasena = hashed_password
        db.commit()
        db.refresh(db_user)
    return db_user

def user_has_password(db: Session, user_id: int) -> bool:
    """
    Verifica si un usuario tiene contraseña establecida
    """
    db_user = db.query(User).filter(User.ID == user_id).first()
    return db_user and db_user.Contrasena is not None and db_user.Contrasena != ""

def get_user_roles(db: Session, user_id: int) -> List[Role]:
    """Obtiene los roles de un usuario"""
    return db.query(Role).join(UserRole).filter(
        UserRole.Usuario_ID == user_id,
        UserRole.Estatus == True,
        Role.Estatus == True
    ).all()