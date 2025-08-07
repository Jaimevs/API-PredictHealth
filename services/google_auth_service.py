import httpx
from typing import Optional
from schemas.google_auth import GoogleUserInfo

async def verify_google_token(token: str) -> Optional[GoogleUserInfo]:
    """
    Verifica el token de Google y obtiene información del usuario
    """
    try:
        # Verificar token con Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Validar que el token sea válido
            if 'sub' not in data or 'email' not in data:
                return None
            
            # Extraer información necesaria
            return GoogleUserInfo(
                google_id=data['sub'],
                email=data['email'],
                name=data.get('name', data['email'].split('@')[0])
            )
            
    except Exception as e:
        print(f"Error verificando token de Google: {e}")
        return None

def generate_username_from_email(email: str) -> str:
    """
    Genera un nombre de usuario único basado en el email
    """
    base_username = email.split('@')[0]
    # Limpiar caracteres especiales
    clean_username = ''.join(c for c in base_username if c.isalnum() or c in '_-')
    return clean_username[:50]  # Limitar a 50 caracteres