from .base_seeder import BaseSeeder
from models.alert import Alert, AlertTypeEnum, PriorityEnum
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class AlertsSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Datos de ejemplo para alertas
        self.alert_templates = [
            {
                'tipo': AlertTypeEnum.FRECUENCIA_ALTA,
                'mensaje': 'Frecuencia cardíaca elevada detectada: {valor} BPM',
                'valor_umbral': 100.0,
                'prioridad': PriorityEnum.ALTA,
                'valores_ejemplo': [105, 110, 115, 120, 125, 130, 135]
            },
            {
                'tipo': AlertTypeEnum.FRECUENCIA_BAJA,
                'mensaje': 'Frecuencia cardíaca baja detectada: {valor} BPM',
                'valor_umbral': 60.0,
                'prioridad': PriorityEnum.MEDIA,
                'valores_ejemplo': [55, 52, 48, 45, 50, 58, 42]
            },
            {
                'tipo': AlertTypeEnum.PRESION_ALTA,
                'mensaje': 'Presión arterial elevada: {valor} mmHg',
                'valor_umbral': 140.0,
                'prioridad': PriorityEnum.ALTA,
                'valores_ejemplo': [145, 150, 155, 160, 165, 170, 180]
            },
            {
                'tipo': AlertTypeEnum.SATURACION_BAJA,
                'mensaje': 'Saturación de oxígeno baja: {valor}%',
                'valor_umbral': 95.0,
                'prioridad': PriorityEnum.CRITICA,
                'valores_ejemplo': [92, 90, 88, 85, 93, 91, 87]
            },
            {
                'tipo': AlertTypeEnum.CAIDA_DETECTADA,
                'mensaje': 'Posible caída detectada - Verificar estado del usuario',
                'valor_umbral': None,
                'prioridad': PriorityEnum.CRITICA,
                'valores_ejemplo': [None] * 7
            },
            {
                'tipo': AlertTypeEnum.MEDICAMENTO,
                'mensaje': 'Recordatorio: Es hora de tomar su medicamento',
                'valor_umbral': None,
                'prioridad': PriorityEnum.MEDIA,
                'valores_ejemplo': [None] * 7
            },
            {
                'tipo': AlertTypeEnum.EJERCICIO,
                'mensaje': 'Meta de actividad física no alcanzada hoy: {valor} pasos',
                'valor_umbral': 10000.0,
                'prioridad': PriorityEnum.BAJA,
                'valores_ejemplo': [8500, 7200, 6800, 5500, 9200, 8800, 7500]
            },
            {
                'tipo': AlertTypeEnum.PERSONALIZADA,
                'mensaje': 'Alerta personalizada: Revisar niveles de estrés elevados',
                'valor_umbral': 80.0,
                'prioridad': PriorityEnum.MEDIA,
                'valores_ejemplo': [85, 90, 88, 92, 87, 95, 83]
            }
        ]
    
    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        try:
            from config.database import engine
            Alert.__table__.create(engine, checkfirst=True)
            logger.info("✅ Tabla de alertas verificada/creada")
        except Exception as e:
            logger.warning(f"⚠️ Error al crear tabla de alertas: {e}")
    
    def generate_sample_alerts(self):
        """Generar alertas de ejemplo para usuarios existentes"""
        alerts = []
        
        # Obtener IDs de usuarios reales de la base de datos
        from models.user import User
        from models.smartwatch import Smartwatch
        
        user_query = self.db.query(User.ID).all()
        user_ids = [user.ID for user in user_query]
        
        if not user_ids:
            logger.warning("⚠️ No se encontraron usuarios en la base de datos. Ejecute primero user_seeder.")
            return []
        
        # Obtener IDs de smartwatches reales de la base de datos
        smartwatch_query = self.db.query(Smartwatch.ID).all()
        smartwatch_ids = [sw.ID for sw in smartwatch_query]
        
        if not smartwatch_ids:
            logger.warning("⚠️ No se encontraron smartwatches en la base de datos. Ejecute primero smartwatch_seeder.")
            return []
        
        logger.info(f"📋 Encontrados {len(user_ids)} usuarios: {user_ids}")
        logger.info(f"⌚ Encontrados {len(smartwatch_ids)} smartwatches: {smartwatch_ids}")
        
        # Generar alertas para cada usuario
        for user_id in user_ids:
            # Cada usuario tendrá entre 3 y 8 alertas
            num_alerts = random.randint(3, 8)
            
            for _ in range(num_alerts):
                template = random.choice(self.alert_templates)
                valor_detectado = random.choice(template['valores_ejemplo'])
                
                # Generar timestamp aleatorio en los últimos 30 días
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                
                # Formatear mensaje con valor si aplica
                mensaje = template['mensaje']
                if valor_detectado is not None:
                    mensaje = mensaje.format(valor=valor_detectado)
                
                # Crear alerta
                alert = Alert(
                    Usuario_ID=user_id,
                    Smartwatch_ID=random.choice(smartwatch_ids),
                    Tipo_alerta=template['tipo'],
                    Mensaje=mensaje,
                    Valor_detectado=valor_detectado,
                    Valor_umbral=template['valor_umbral'],
                    Prioridad=template['prioridad'],
                    Timestamp_alerta=timestamp,
                    Estatus=random.choice([True, True, True, False]),  # 75% activas
                    Fecha_Registro=timestamp
                )
                
                alerts.append(alert)
        
        return alerts
    
    def run(self, clear_first=False, table_names=None):
        """Ejecutar el seeder de alertas"""
        try:
            if clear_first and table_names:
                logger.info("🗑️ Limpiando datos existentes de alertas...")
                self.clear_tables(table_names)
            
            logger.info("📢 Generando alertas de ejemplo...")
            
            # Generar alertas
            alerts = self.generate_sample_alerts()
            
            # Insertar en la base de datos
            logger.info(f"💾 Insertando {len(alerts)} alertas...")
            self.db.add_all(alerts)
            self.db.commit()
            
            # Estadísticas
            total_alerts = len(alerts)
            alerts_by_priority = {}
            alerts_by_type = {}
            active_alerts = sum(1 for alert in alerts if alert.Estatus)
            
            for alert in alerts:
                # Contar por prioridad
                priority = alert.Prioridad.value if alert.Prioridad else 'Sin prioridad'
                alerts_by_priority[priority] = alerts_by_priority.get(priority, 0) + 1
                
                # Contar por tipo
                alert_type = alert.Tipo_alerta.value
                alerts_by_type[alert_type] = alerts_by_type.get(alert_type, 0) + 1
            
            logger.info(f"✅ Alertas creadas exitosamente:")
            logger.info(f"   📊 Total: {total_alerts}")
            logger.info(f"   🟢 Activas: {active_alerts}")
            logger.info(f"   🔴 Inactivas: {total_alerts - active_alerts}")
            
            logger.info("📈 Por prioridad:")
            for priority, count in sorted(alerts_by_priority.items()):
                logger.info(f"   - {priority}: {count}")
            
            logger.info("🏷️ Por tipo:")
            for alert_type, count in sorted(alerts_by_type.items()):
                logger.info(f"   - {alert_type}: {count}")
                
        except Exception as e:
            logger.error(f"❌ Error durante el seeding de alertas: {str(e)}")
            self.db.rollback()
            raise e

def main():
    """Función para ejecutar el seeder de forma independiente"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Seeder de Alertas')
    parser.add_argument('--clear', action='store_true', help='Limpiar datos existentes')
    args = parser.parse_args()
    
    try:
        with AlertsSeeder() as seeder:
            seeder.create_tables()
            seeder.run(
                clear_first=args.clear,
                table_names=['tbb_alertas'] if args.clear else None
            )
        logger.info("✅ Seeder de alertas completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()