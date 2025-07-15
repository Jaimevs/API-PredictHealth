# models/__init__.py
from .user import User
from .role import Role
from .person import Person
from .health_profile import HealthProfile
from .smartwatch import Smartwatch
from .heart_measurement import HeartMeasurement
from .physical_activity import PhysicalActivity
from .alert import Alert
from .user_role import UserRole

# Exporta todos los modelos para que estén disponibles
__all__ = [
    'User', 
    'Role', 
    'Person', 
    'HealthProfile', 
    'Smartwatch', 
    'HeartMeasurement', 
    'PhysicalActivity', 
    'Alert', 
    'UserRole'
]