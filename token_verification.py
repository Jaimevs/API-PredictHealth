# token_verification.py
import os
import json
import time
import uuid
from datetime import datetime, timedelta
from config.settings import settings

# Archivo para almacenar los registros pendientes
PENDING_REGISTRATIONS_FILE = "pending_registrations.json"
# Tiempo de expiración (24 horas)
EXPIRATION_TIME = settings.VERIFICATION_TOKEN_EXPIRE_HOURS * 60 * 60

def store_pending_registration(user_data: dict, verification_code: str):
    """
    Almacena los datos del usuario pendiente de verificación junto con su código
    Adaptado para tu estructura de BD
    """
    # Generar un token único
    token = str(uuid.uuid4())
    
    # Crear estructura para almacenar
    pending_data = {
        "user_data": user_data,
        "verification_code": verification_code,
        "created_at": time.time(),
        "expires_at": time.time() + EXPIRATION_TIME
    }
    
    # Cargar registros existentes
    pending_registrations = {}
    if os.path.exists(PENDING_REGISTRATIONS_FILE):
        try:
            with open(PENDING_REGISTRATIONS_FILE, "r") as f:
                pending_registrations = json.load(f)
        except json.JSONDecodeError:
            pending_registrations = {}
    
    # Limpiar registros expirados antes de agregar uno nuevo
    clean_expired_registrations(pending_registrations)
    
    # Añadir nuevo registro
    pending_registrations[token] = pending_data
    
    # Guardar actualización
    with open(PENDING_REGISTRATIONS_FILE, "w") as f:
        json.dump(pending_registrations, f, indent=2)
    
    return token

def verify_code(email: str, code: str):
    """
    Verifica si el código proporcionado es válido para el correo electrónico
    Retorna el token si es válido, None si no lo es
    Adaptado para usar 'correo_electronico' en lugar de 'email'
    """
    if not os.path.exists(PENDING_REGISTRATIONS_FILE):
        return None
    
    try:
        with open(PENDING_REGISTRATIONS_FILE, "r") as f:
            pending_registrations = json.load(f)
    except json.JSONDecodeError:
        return None
    
    # Buscar registro por email y código
    for token, data in pending_registrations.items():
        user_data = data.get("user_data", {})
        if (user_data.get("correo_electronico") == email and  # Cambiado a correo_electronico
            data.get("verification_code") == code and 
            data.get("expires_at", 0) > time.time()):
            return token  # Retornamos el token para poder eliminar el registro después
    
    return None

def get_pending_registration(token: str):
    """
    Obtiene los datos de un registro pendiente por token
    """
    if not os.path.exists(PENDING_REGISTRATIONS_FILE):
        return None
    
    try:
        with open(PENDING_REGISTRATIONS_FILE, "r") as f:
            pending_registrations = json.load(f)
    except json.JSONDecodeError:
        return None
    
    # Verificar si el token existe y no ha expirado
    if token in pending_registrations:
        data = pending_registrations[token]
        if data.get("expires_at", 0) > time.time():
            return data.get("user_data")
    
    return None

def remove_pending_registration(token: str):
    """
    Elimina un registro pendiente después de la verificación
    """
    if not os.path.exists(PENDING_REGISTRATIONS_FILE):
        return False
    
    try:
        with open(PENDING_REGISTRATIONS_FILE, "r") as f:
            pending_registrations = json.load(f)
    except json.JSONDecodeError:
        return False
    
    # Eliminar registro si existe
    if token in pending_registrations:
        del pending_registrations[token]
        
        # Guardar actualización
        with open(PENDING_REGISTRATIONS_FILE, "w") as f:
            json.dump(pending_registrations, f, indent=2)
        
        return True
    
    return False

def clean_expired_registrations(pending_registrations: dict = None):
    """
    Limpia registros expirados del archivo
    """
    if pending_registrations is None:
        if not os.path.exists(PENDING_REGISTRATIONS_FILE):
            return
        
        try:
            with open(PENDING_REGISTRATIONS_FILE, "r") as f:
                pending_registrations = json.load(f)
        except json.JSONDecodeError:
            return
    
    current_time = time.time()
    expired_tokens = []
    
    # Identificar tokens expirados
    for token, data in pending_registrations.items():
        if data.get("expires_at", 0) <= current_time:
            expired_tokens.append(token)
    
    # Eliminar tokens expirados
    for token in expired_tokens:
        del pending_registrations[token]
    
    # Guardar si se eliminaron registros
    if expired_tokens:
        with open(PENDING_REGISTRATIONS_FILE, "w") as f:
            json.dump(pending_registrations, f, indent=2)
        print(f"Se eliminaron {len(expired_tokens)} registros expirados")