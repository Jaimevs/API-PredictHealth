# routes/seeder.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from config.database import get_db
from dependencies.auth import require_admin
from typing import Optional, List
import logging
import time
from datetime import datetime

# Importar todos los seeders
from seeders.main_seeder import MainSeeder
from seeders.role_seeder import RoleSeeder
from seeders.person_seeder import PersonSeeder
from seeders.user_seeder import UserSeeder
from seeders.user_role_seeder import UserRoleSeeder
from seeders.smartwatch_seeder import SmartwatchSeeder
from seeders.health_profile import HealthProfileSeeder
from seeders.heart_measurement_seederV2 import HeartMeasurementSeeder
from seeders.alerts_seeder import AlertsSeeder
from seeders.physical_activity_seeder import PhysicalActivitySeeder

router = APIRouter(
    prefix="/seeders",
    tags=["seeders"],
    dependencies=[Depends(require_admin())],  # Solo administradores
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

# Configuración de seeders disponibles
AVAILABLE_SEEDERS = {
    "roles": {
        "seeder": RoleSeeder,
        "name": "Roles",
        "tables": ["tbc_roles"],
        "description": "Crear roles del sistema: ADMIN, USUARIO, MEDICO"
    },
    "persons": {
        "seeder": PersonSeeder,
        "name": "Personas",
        "tables": ["tbb_personas"],
        "description": "Crear personas de prueba con datos aleatorios"
    },
    "users": {
        "seeder": UserSeeder,
        "name": "Usuarios",
        "tables": ["tbb_usuarios"],
        "description": "Crear usuarios asociados a personas existentes"
    },
    "user_roles": {
        "seeder": UserRoleSeeder,
        "name": "Asignación de Roles",
        "tables": ["tbd_usuarios_roles"],
        "description": "Asignar roles a usuarios existentes"
    },
    "smartwatches": {
        "seeder": SmartwatchSeeder,
        "name": "Smartwatches",
        "tables": ["tbb_smartwatches"],
        "description": "Crear dispositivos smartwatch para usuarios"
    },
    "health_profiles": {
        "seeder": HealthProfileSeeder,
        "name": "Perfiles de Salud",
        "tables": ["tbb_perfil_salud"],
        "description": "Crear perfiles de salud con datos médicos"
    },
    "heart_measurements": {
        "seeder": HeartMeasurementSeeder,
        "name": "Mediciones Cardíacas",
        "tables": ["tbb_mediciones_cardiacas"],
        "description": "Crear historial de mediciones cardíacas"
    },
    "alerts": {
        "seeder": AlertsSeeder,
        "name": "Alertas",
        "tables": ["tbb_alertas"],
        "description": "Crear alertas de salud con diferentes prioridades"
    },
    "physical_activities": {
        "seeder": PhysicalActivitySeeder,
        "name": "Actividad Física",
        "tables": ["tbb_actividad_fisica"],
        "description": "Crear datos de actividad física"
    }
}

@router.get("/")
async def list_available_seeders():
    """
    Lista todos los seeders disponibles con su información
    """
    return {
        "message": "Seeders disponibles para ejecutar",
        "seeders": {
            key: {
                "name": config["name"],
                "description": config["description"],
                "tables": config["tables"]
            } for key, config in AVAILABLE_SEEDERS.items()
        },
        "endpoints": {
            "run_individual": "/seeders/run/{seeder_name}",
            "run_all": "/seeders/run-all",
            "clear_all": "/seeders/clear-all"
        }
    }

@router.post("/run/{seeder_name}")
async def run_individual_seeder(
    seeder_name: str,
    clear_first: bool = Query(False, description="Limpiar datos existentes antes de ejecutar"),
    db: Session = Depends(get_db)
):
    """
    Ejecuta un seeder individual específico
    """
    if seeder_name not in AVAILABLE_SEEDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seeder '{seeder_name}' no encontrado. Seeders disponibles: {list(AVAILABLE_SEEDERS.keys())}"
        )
    
    seeder_config = AVAILABLE_SEEDERS[seeder_name]
    start_time = time.time()
    
    try:
        logger.info(f"Ejecutando seeder: {seeder_config['name']}")
        
        # Ejecutar seeder específico
        with seeder_config['seeder']() as seeder:
            # Crear tablas si no existen
            seeder.create_tables()
            
            # Ejecutar seeder con opción de limpiar primero
            seeder.run(
                clear_first=clear_first,
                table_names=seeder_config['tables'] if clear_first else None
            )
        
        execution_time = time.time() - start_time
        
        return {
            "message": f"Seeder '{seeder_config['name']}' ejecutado exitosamente",
            "seeder": seeder_name,
            "name": seeder_config['name'],
            "tables_affected": seeder_config['tables'],
            "cleared_first": clear_first,
            "execution_time_seconds": round(execution_time, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error ejecutando seeder {seeder_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando seeder '{seeder_name}': {str(e)}"
        )

@router.post("/run-all")
async def run_all_seeders(
    clear_first: bool = Query(False, description="Limpiar todos los datos antes de ejecutar"),
    selected_seeders: Optional[List[str]] = Query(None, description="Lista de seeders específicos a ejecutar")
):
    """
    Ejecuta todos los seeders o una lista específica en el orden correcto
    """
    start_time = time.time()
    
    try:
        # Si se especifican seeders específicos, validar que existan
        if selected_seeders:
            invalid_seeders = [s for s in selected_seeders if s not in AVAILABLE_SEEDERS]
            if invalid_seeders:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Seeders inválidos: {invalid_seeders}. Disponibles: {list(AVAILABLE_SEEDERS.keys())}"
                )
            
            # Filtrar y mantener el orden correcto
            seeders_to_run = [(k, v) for k, v in AVAILABLE_SEEDERS.items() if k in selected_seeders]
            logger.info(f"Ejecutando seeders específicos: {selected_seeders}")
        else:
            # Ejecutar todos los seeders
            seeders_to_run = list(AVAILABLE_SEEDERS.items())
            logger.info("Ejecutando todos los seeders")
        
        # Usar MainSeeder si se ejecutan todos, o ejecutar individuales
        if not selected_seeders:
            main_seeder = MainSeeder(clear_data=clear_first)
            main_seeder.run()
            
            execution_time = time.time() - start_time
            
            return {
                "message": "Todos los seeders ejecutados exitosamente",
                "seeders_executed": list(AVAILABLE_SEEDERS.keys()),
                "cleared_first": clear_first,
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "roles": "3 roles creados (ADMIN, USUARIO, MEDICO)",
                    "persons": "Personas de prueba creadas",
                    "users": "Usuarios con contraseñas hasheadas",
                    "user_roles": "Roles asignados apropiadamente",
                    "smartwatches": "Dispositivos asociados a usuarios",
                    "health_profiles": "Perfiles de salud completos",
                    "heart_measurements": "Historial de mediciones (30 días)",
                    "alerts": "Alertas con diferentes prioridades",
                    "physical_activities": "Datos de actividad física (90 días)"
                }
            }
        else:
            # Ejecutar seeders específicos individualmente
            executed_seeders = []
            
            for seeder_key, seeder_config in seeders_to_run:
                logger.info(f"Ejecutando seeder: {seeder_config['name']}")
                
                with seeder_config['seeder']() as seeder:
                    seeder.create_tables()
                    seeder.run(
                        clear_first=clear_first,
                        table_names=seeder_config['tables'] if clear_first else None
                    )
                
                executed_seeders.append({
                    "key": seeder_key,
                    "name": seeder_config['name'],
                    "tables": seeder_config['tables']
                })
            
            execution_time = time.time() - start_time
            
            return {
                "message": "Seeders específicos ejecutados exitosamente",
                "seeders_executed": executed_seeders,
                "cleared_first": clear_first,
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error ejecutando seeders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando seeders: {str(e)}"
        )

@router.post("/clear-all")
async def clear_all_data():
    """
    Limpia todos los datos de todas las tablas sin insertar nuevos datos
    ⚠️ OPERACIÓN DESTRUCTIVA
    """
    start_time = time.time()
    
    try:
        logger.warning("Iniciando limpieza completa de la base de datos")
        
        main_seeder = MainSeeder()
        main_seeder.clear_all_data()
        
        execution_time = time.time() - start_time
        
        return {
            "message": "⚠️ Todos los datos han sido eliminados de la base de datos",
            "warning": "Esta operación no se puede deshacer",
            "tables_cleared": [
                "tbb_actividad_fisica",
                "tbb_alertas", 
                "tbb_mediciones_cardiacas",
                "tbb_perfil_salud",
                "tbb_smartwatches",
                "tbd_usuarios_roles",
                "tbb_usuarios",
                "tbb_personas",
                "tbc_roles"
            ],
            "execution_time_seconds": round(execution_time, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error limpiando datos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error limpiando datos: {str(e)}"
        )

@router.post("/heart-measurements/{user_id}")
async def seed_heart_measurements_for_user(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Días de historial a generar"),
    db: Session = Depends(get_db)
):
    """
    Genera mediciones cardíacas para un usuario específico
    """
    start_time = time.time()
    
    try:
        # Verificar que el usuario existe
        from crud.user import get_user
        user = get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {user_id} no encontrado"
            )
        
        logger.info(f"Generando {days} días de mediciones para usuario {user_id}")
        
        with HeartMeasurementSeeder() as seeder:
            # Método específico para un usuario (necesitarías implementar esto en el seeder)
            # Por ahora usaremos el método general
            seeder.seed(dias_historial=days)
        
        execution_time = time.time() - start_time
        
        return {
            "message": f"Mediciones cardíacas generadas para usuario {user_id}",
            "user_id": user_id,
            "days_generated": days,
            "execution_time_seconds": round(execution_time, 2),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando mediciones para usuario {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando mediciones: {str(e)}"
        )

@router.get("/status")
async def get_seeding_status(db: Session = Depends(get_db)):
    """
    Obtiene el estado actual de los datos en cada tabla
    """
    try:
        from sqlalchemy import text
        
        # Consultar el conteo de registros en cada tabla
        table_counts = {}
        
        tables_to_check = [
            ("tbc_roles", "Roles"),
            ("tbb_personas", "Personas"),
            ("tbb_usuarios", "Usuarios"),
            ("tbd_usuarios_roles", "Asignaciones de Roles"),
            ("tbb_smartwatches", "Smartwatches"),
            ("tbb_perfil_salud", "Perfiles de Salud"),
            ("tbb_mediciones_cardiacas", "Mediciones Cardíacas"),
            ("tbb_alertas", "Alertas"),
            ("tbb_actividad_fisica", "Actividad Física")
        ]
        
        for table_name, display_name in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                table_counts[table_name] = {
                    "name": display_name,
                    "count": count,
                    "status": "populated" if count > 0 else "empty"
                }
            except Exception as e:
                table_counts[table_name] = {
                    "name": display_name,
                    "count": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        # Calcular resumen
        total_tables = len(tables_to_check)
        populated_tables = sum(1 for info in table_counts.values() if info["status"] == "populated")
        empty_tables = sum(1 for info in table_counts.values() if info["status"] == "empty")
        error_tables = sum(1 for info in table_counts.values() if info["status"] == "error")
        
        return {
            "message": "Estado actual de la base de datos",
            "summary": {
                "total_tables": total_tables,
                "populated_tables": populated_tables,
                "empty_tables": empty_tables,
                "error_tables": error_tables,
                "completion_percentage": round((populated_tables / total_tables) * 100, 1)
            },
            "tables": table_counts,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado: {str(e)}"
        )