from .base_seeder import BaseSeeder
from models.role import Role
import logging

logger = logging.getLogger(__name__)

class RoleSeeder(BaseSeeder):
    def seed(self):
        """Seed inicial para los roles del sistema"""
        logger.info("Iniciando seeding de roles...")
        
        roles_data = [
            {
                'Nombre': 'ADMIN',
                'Descripcion': 'Administrador del sistema con acceso completo',
                'Estatus': True
            },
            {
                'Nombre': 'USUARIO',
                'Descripcion': 'Usuario estándar con acceso a sus datos',
                'Estatus': True
            },
            {
                'Nombre': 'MEDICO',
                'Descripcion': 'Profesional de la salud con acceso a datos médicos',
                'Estatus': True
            }
        ]
        
        for role_data in roles_data:
            # Verificar si el rol ya existe
            existing_role = self.db.query(Role).filter(Role.Nombre == role_data['Nombre']).first()
            
            if not existing_role:
                role = Role(**role_data)
                self.db.add(role)
                logger.info(f"Rol creado: {role_data['Nombre']}")
            else:
                logger.info(f"Rol ya existe: {role_data['Nombre']}")
        
        logger.info("Seeding de roles completado")

if __name__ == "__main__":
    with RoleSeeder() as seeder:
        seeder.create_tables()
        seeder.run(clear_first=True, table_names=['tbc_roles'])