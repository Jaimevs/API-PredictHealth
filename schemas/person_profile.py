from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

class PersonProfileUpdate(BaseModel):
    """Esquema para actualizar datos personales del usuario"""
    nombre: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: str  # formato: "YYYY-MM-DD"
    genero: str  # "H", "M", o "N/B"
    
    @validator('nombre')
    def nombre_must_be_valid(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        if len(v) > 80:
            raise ValueError('El nombre debe tener máximo 80 caracteres')
        return v.strip()
    
    @validator('primer_apellido')
    def primer_apellido_must_be_valid(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('El primer apellido debe tener al menos 2 caracteres')
        if len(v) > 80:
            raise ValueError('El primer apellido debe tener máximo 80 caracteres')
        return v.strip()
    
    @validator('segundo_apellido')
    def segundo_apellido_must_be_valid(cls, v):
        if v is not None and len(v.strip()) > 80:
            raise ValueError('El segundo apellido debe tener máximo 80 caracteres')
        return v.strip() if v else None
    
    @validator('genero')
    def genero_must_be_valid(cls, v):
        if v not in ["H", "M", "N/B"]:
            raise ValueError('El género debe ser "H", "M" o "N/B"')
        return v
    
    @validator('fecha_nacimiento')
    def fecha_must_be_valid(cls, v):
        try:
            from datetime import datetime
            fecha = datetime.strptime(v, "%Y-%m-%d").date()
            
            # Validar que no sea fecha futura
            if fecha > datetime.now().date():
                raise ValueError('La fecha de nacimiento no puede ser futura')
            
            # Validar que sea una edad razonable (mayor a 5 años, menor a 120)
            from datetime import timedelta
            min_date = datetime.now().date() - timedelta(days=120*365)
            max_date = datetime.now().date() - timedelta(days=5*365)
            
            if fecha < min_date:
                raise ValueError('Fecha de nacimiento no válida (muy antigua)')
            if fecha > max_date:
                raise ValueError('Debe ser mayor de 5 años')
            
            return v
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD')
            raise e

class PersonProfileResponse(BaseModel):
    """Esquema para respuesta de perfil personal"""
    ID: int
    Nombre: str
    Primer_Apellido: str
    Segundo_Apellido: Optional[str]
    Fecha_Nacimiento: date
    Genero: str
    Estatus: bool
    
    class Config:
        from_attributes = True