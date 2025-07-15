# seeders/__init__.py
"""
Módulo de seeders para la aplicación.
Este archivo importa todos los seeders disponibles.
"""

# Importar solo los seeders, NO los modelos
from .main_seeder import MainSeeder
from .role_seeder import RoleSeeder
from .person_seeder import PersonSeeder
from .user_seeder import UserSeeder
from .user_role_seeder import UserRoleSeeder

__all__ = [
    'MainSeeder',
    'RoleSeeder',
    'PersonSeeder', 
    'UserSeeder',
    'UserRoleSeeder'
]