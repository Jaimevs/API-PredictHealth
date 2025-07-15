from sqlalchemy.orm import Session
from sqlalchemy import text
from config.database import SessionLocal, Base, engine 
from datetime import datetime, date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseSeeder:
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
            logger.error(f"Error durante el seeding: {exc_val}")
        else:
            self.db.commit()
        self.db.close()
    
    def create_tables(self):
        """Crear todas las tablas"""
        logger.info("Creando tablas...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas exitosamente")
    
    def clear_tables(self, table_names: list):
        """Limpiar tablas específicas y reiniciar AUTO_INCREMENT"""
        try:
            # Desactivar verificación de claves foráneas temporalmente
            self.db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            for table_name in table_names:
                logger.info(f"Limpiando tabla {table_name}...")
                
                # Usar TRUNCATE que elimina datos y reinicia AUTO_INCREMENT automáticamente
                self.db.execute(text(f"TRUNCATE TABLE {table_name}"))
                
                logger.info(f"Tabla {table_name} limpiada y contador reiniciado")
            
            # Reactivar verificación de claves foráneas
            self.db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            self.db.commit()
            logger.info("Tablas limpiadas")
            
        except Exception as e:
            logger.error(f"Error limpiando tablas: {e}")
            self.db.rollback()
            raise
    
    def seed(self):
        """Método que debe ser implementado por cada seeder"""
        raise NotImplementedError("Cada seeder debe implementar el método seed()")
    
    def clear_all_data(self):
        """Limpiar TODAS las tablas de la base de datos"""
        try:
            logger.info("🗑️  Iniciando limpieza completa de la base de datos...")
            
            # Orden de limpieza: primero tablas con FK, luego tablas principales
            tables_to_clear = [
                'tbd_usuarios_roles',      # Relaciones
                'tbb_heart_measurements',  # Dependiente de usuario
                'tbb_physical_activities', # Dependiente de usuario
                'tbb_alerts',             # Dependiente de usuario
                'tbb_smartwatches',       # Dependiente de usuario
                'tbb_health_profiles',    # Dependiente de usuario
                'tbb_usuarios',           # Usuario principal
                'tbb_personas',           # Personas
                'tbc_roles'               # Roles base
            ]
            
            self.clear_tables(tables_to_clear)
            logger.info("✅ Base de datos limpiada completamente")
            
        except Exception as e:
            logger.error(f"❌ Error limpiando la base de datos: {e}")
            raise

    def run(self, clear_first=False, table_names=None, clear_only=False):
        """Ejecutar el seeder"""
        try:
            if clear_only:
                self.clear_all_data()
                return  # No ejecutar seeding, solo limpiar
                
            if clear_first and table_names:
                self.clear_tables(table_names)
            
            self.seed()
            logger.info("Seeding completado exitosamente")
            
        except Exception as e:
            logger.error(f"Error durante el seeding: {str(e)}")
            raise e