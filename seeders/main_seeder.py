#!/usr/bin/env python3
"""
Seeder principal que ejecuta todos los seeders en el orden correcto
"""

from .role_seeder import RoleSeeder
from .person_seeder import PersonSeeder
from .user_seeder import UserSeeder
from .user_role_seeder import UserRoleSeeder
from .smartwatch_seeder import SmartwatchSeeder
from .health_profile import HealthProfileSeeder
from .alerts_seeder import AlertsSeeder
from .physical_activity_seeder import PhysicalActivitySeeder
from .base_seeder import BaseSeeder
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MainSeeder:
    def __init__(self, clear_data=False):
        self.clear_data = clear_data
        self.seeders = [
            {
                'seeder': RoleSeeder,
                'name': 'Roles',
                'tables': ['tbc_roles']
            },
            {
                'seeder': PersonSeeder,
                'name': 'Personas',
                'tables': ['tbb_personas']
            },
            {
                'seeder': UserSeeder,
                'name': 'Usuarios',
                'tables': ['tbb_usuarios']
            },
            {
                'seeder': UserRoleSeeder,
                'name': 'Asignación de Roles',
                'tables': ['tbd_usuarios_roles']
            },
            {
                'seeder': SmartwatchSeeder,
                'name': 'Smartwatches',
                'tables': ['tbb_smartwatches']
            },
            {
                'seeder': HealthProfileSeeder,
                'name': 'Perfiles de Salud',
                'tables': ['tbb_perfil_salud']
            },
            {
                'seeder': AlertsSeeder,
                'name': 'Alertas',
                'tables': ['tbb_alertas']
            },
            {
                'seeder': PhysicalActivitySeeder,
                'name': 'Actividad Física',
                'tables': ['tbb_actividad_fisica']
            }
        ]
    
    def clear_all_data(self):
        """Limpiar TODAS las tablas de la base de datos sin insertar datos"""
        logger.warning("⚠️  MODO DESTRUCTIVO: Los datos existentes serán eliminados")
        confirm = input("¿Está seguro que desea continuar? (y/N): ")
        
        if confirm.lower() != 'y':
            logger.info("❌ Operación cancelada")
            return
        
        try:
            logger.info("🗑️  === INICIANDO LIMPIEZA COMPLETA ===")
            
            with BaseSeeder() as base_seeder:
                # Agregar la tabla de perfiles de salud a la limpieza
                tables_to_clear = [
                    'tbb_actividad_fisica',   # Actividad física
                    'tbb_alertas',            # Alertas
                    'tbb_mediciones_cardiacas', # Mediciones cardíacas
                    'tbb_perfil_salud',       # Perfiles de salud
                    'tbb_smartwatches',       # Smartwatches
                    'tbd_usuarios_roles',     # Relaciones usuario-rol
                    'tbb_usuarios',           # Usuario principal
                    'tbb_personas',           # Personas
                    'tbc_roles',              # Roles base
                ]
                
                logger.info("Limpiando tablas existentes y reiniciando contadores...")
                base_seeder.clear_tables(tables_to_clear)
                
            logger.info("✅ === LIMPIEZA COMPLETA EXITOSA ===")
            logger.info("Todas las tablas existentes han sido limpiadas y los contadores reiniciados a 1")
                
        except Exception as e:
            logger.error(f"❌ Error durante la limpieza: {str(e)}")
            sys.exit(1)
    
    def run(self):
        """Ejecutar todos los seeders en orden"""
        logger.info("=== INICIANDO SEEDING COMPLETO ===")
        
        try:
            for seeder_config in self.seeders:
                logger.info(f"\n--- Ejecutando seeder: {seeder_config['name']} ---")
                
                with seeder_config['seeder']() as seeder:
                    # Crear tablas si no existen
                    seeder.create_tables()
                    
                    # Ejecutar seeder
                    seeder.run(
                        clear_first=self.clear_data,
                        table_names=seeder_config['tables'] if self.clear_data else None
                    )
                
                logger.info(f"✅ Seeder {seeder_config['name']} completado exitosamente")
            
            logger.info("\n=== SEEDING COMPLETO EXITOSO ===")
            logger.info("Datos de prueba creados:")
            logger.info("- 3 Roles: ADMIN, USUARIO, MEDICO")
            logger.info("- 8 Personas de prueba")
            logger.info("- 8 Usuarios con contraseñas hasheadas")
            logger.info("- Asignaciones de roles apropiadas")
            logger.info("- Smartwatches asociados a usuarios")
            logger.info("- Perfiles de salud para todos los usuarios")
            logger.info("- Alertas de salud con diferentes prioridades")
            logger.info("- Datos de actividad física (90 días de historial)")
            
        except Exception as e:
            logger.error(f"❌ Error durante el seeding: {str(e)}")
            sys.exit(1)

def main():
    """Función principal para ejecutar desde línea de comandos"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejecutar seeders de la base de datos')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Limpiar datos existentes antes de hacer el seeding'
    )
    parser.add_argument(
        '--clear-only',
        action='store_true',
        help='Solo limpiar las tablas sin insertar nuevos datos'
    )
    parser.add_argument(
        '--health-only',
        action='store_true',
        help='Solo ejecutar el seeder de perfiles de salud'
    )
    
    args = parser.parse_args()
    
    # Validar que no se usen opciones incompatibles
    if args.clear and args.clear_only:
        logger.error("❌ No puede usar --clear y --clear-only al mismo tiempo")
        sys.exit(1)
    
    if args.health_only:
        # Solo ejecutar el seeder de perfiles de salud
        logger.info("🏥 Ejecutando solo el seeder de perfiles de salud...")
        try:
            with HealthProfileSeeder() as seeder:
                seeder.create_tables()
                seeder.run(clear_first=False)
            logger.info("✅ Seeder de perfiles de salud completado")
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            sys.exit(1)
        return
    
    main_seeder = MainSeeder(clear_data=args.clear)
    
    if args.clear_only:
        # Solo limpiar, no ejecutar seeders
        main_seeder.clear_all_data()
    elif args.clear:
        # Limpiar y luego ejecutar seeders
        logger.warning("⚠️  MODO DESTRUCTIVO: Los datos existentes serán eliminados")
        confirm = input("¿Está seguro que desea continuar? (y/N): ")
        if confirm.lower() != 'y':
            logger.info("Operación cancelada")
            sys.exit(0)
        main_seeder.run()
    else:
        # Solo ejecutar seeders
        main_seeder.run()

if __name__ == "__main__":
    main()