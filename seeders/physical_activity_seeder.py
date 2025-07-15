from .base_seeder import BaseSeeder
from models.physical_activity import PhysicalActivity
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class PhysicalActivitySeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Perfiles de actividad física típicos
        self.activity_profiles = {
            'sedentario': {
                'pasos': (2000, 5000),
                'distancia': (1.5, 3.5),
                'calorias': (1200, 1800),
                'minutos_actividad': (15, 45),
                'pisos': (0, 3)
            },
            'moderado': {
                'pasos': (5000, 8000),
                'distancia': (3.5, 6.0),
                'calorias': (1800, 2400),
                'minutos_actividad': (45, 90),
                'pisos': (3, 8)
            },
            'activo': {
                'pasos': (8000, 12000),
                'distancia': (6.0, 9.0),
                'calorias': (2400, 3000),
                'minutos_actividad': (90, 150),
                'pisos': (8, 15)
            },
            'muy_activo': {
                'pasos': (12000, 20000),
                'distancia': (9.0, 15.0),
                'calorias': (3000, 4000),
                'minutos_actividad': (150, 240),
                'pisos': (15, 25)
            }
        }
        
        # Variaciones por día de la semana
        self.weekly_variations = {
            0: 1.1,  # Lunes - más activo
            1: 1.0,  # Martes - normal
            2: 0.95, # Miércoles - ligeramente menos
            3: 1.05, # Jueves - un poco más
            4: 0.9,  # Viernes - menos activo
            5: 1.2,  # Sábado - más activo (fin de semana)
            6: 0.8   # Domingo - día de descanso
        }
    
    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        try:
            from config.database import engine
            PhysicalActivity.__table__.create(engine, checkfirst=True)
            logger.info("✅ Tabla de actividad física verificada/creada")
        except Exception as e:
            logger.warning(f"⚠️ Error al crear tabla de actividad física: {e}")
    
    def generate_daily_activity(self, profile_name, date, user_id, smartwatch_id):
        """Generar actividad física para un día específico"""
        profile = self.activity_profiles[profile_name]
        
        # Aplicar variación del día de la semana
        day_variation = self.weekly_variations[date.weekday()]
        
        # Generar valores base con variación
        pasos = int(random.randint(*profile['pasos']) * day_variation)
        distancia = round(random.uniform(*profile['distancia']) * day_variation, 2)
        calorias = int(random.randint(*profile['calorias']) * day_variation)
        minutos_actividad = int(random.randint(*profile['minutos_actividad']) * day_variation)
        pisos = int(random.randint(*profile['pisos']) * day_variation)
        
        # Añadir algo de variabilidad natural (±15%)
        variation_factor = random.uniform(0.85, 1.15)
        pasos = max(0, int(pasos * variation_factor))
        distancia = max(0, round(distancia * variation_factor, 2))
        calorias = max(500, int(calorias * variation_factor))  # Mínimo 500 calorías base
        minutos_actividad = max(0, int(minutos_actividad * variation_factor))
        pisos = max(0, int(pisos * variation_factor))
        
        # Crear timestamp para el día
        timestamp = datetime.combine(date, datetime.min.time()) + timedelta(
            hours=random.randint(6, 22),
            minutes=random.randint(0, 59)
        )
        
        return PhysicalActivity(
            Usuario_ID=user_id,
            Smartwatch_ID=smartwatch_id,
            Pasos=pasos,
            Distancia_km=distancia,
            Calorias_quemadas=calorias,
            Minutos_actividad=minutos_actividad,
            Pisos_subidos=pisos,
            Estatus=True,
            Fecha_Registro=timestamp
        )
    
    def generate_sample_activities(self):
        """Generar actividades físicas de ejemplo para usuarios existentes"""
        activities = []
        
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
        
        # Asignar perfiles de actividad a usuarios
        profile_names = list(self.activity_profiles.keys())
        user_profiles = {}
        for user_id in user_ids:
            # Distribuir perfiles de manera realista
            if user_id <= 2:
                user_profiles[user_id] = 'sedentario'
            elif user_id <= 5:
                user_profiles[user_id] = 'moderado'
            elif user_id <= 7:
                user_profiles[user_id] = 'activo'
            else:
                user_profiles[user_id] = 'muy_activo'
        
        # Generar datos para los últimos 90 días
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        current_date = start_date
        while current_date <= end_date:
            for user_id in user_ids:
                # 85% de probabilidad de tener datos para cada día
                if random.random() < 0.85:
                    activity = self.generate_daily_activity(
                        user_profiles[user_id],
                        current_date,
                        user_id,
                        random.choice(smartwatch_ids)
                    )
                    activities.append(activity)
            
            current_date += timedelta(days=1)
        
        return activities
    
    def run(self, clear_first=False, table_names=None):
        """Ejecutar el seeder de actividad física"""
        try:
            if clear_first and table_names:
                logger.info("🗑️ Limpiando datos existentes de actividad física...")
                self.clear_tables(table_names)
            
            logger.info("🏃 Generando datos de actividad física...")
            
            # Generar actividades
            activities = self.generate_sample_activities()
            
            # Insertar en la base de datos en lotes para mejor rendimiento
            logger.info(f"💾 Insertando {len(activities)} registros de actividad...")
            
            batch_size = 1000
            for i in range(0, len(activities), batch_size):
                batch = activities[i:i + batch_size]
                self.db.add_all(batch)
                self.db.commit()
                logger.info(f"   ✅ Procesado lote {i//batch_size + 1}/{(len(activities)-1)//batch_size + 1}")
            
            # Estadísticas
            total_activities = len(activities)
            
            # Calcular estadísticas por usuario
            user_stats = {}
            for activity in activities:
                user_id = activity.Usuario_ID
                if user_id not in user_stats:
                    user_stats[user_id] = {
                        'count': 0,
                        'total_pasos': 0,
                        'total_distancia': 0,
                        'total_calorias': 0,
                        'total_minutos': 0,
                        'total_pisos': 0
                    }
                
                stats = user_stats[user_id]
                stats['count'] += 1
                stats['total_pasos'] += activity.Pasos or 0
                stats['total_distancia'] += float(activity.Distancia_km or 0)
                stats['total_calorias'] += activity.Calorias_quemadas or 0
                stats['total_minutos'] += activity.Minutos_actividad or 0
                stats['total_pisos'] += activity.Pisos_subidos or 0
            
            logger.info(f"✅ Actividades físicas creadas exitosamente:")
            logger.info(f"   📊 Total de registros: {total_activities}")
            logger.info(f"   👥 Usuarios con datos: {len(user_stats)}")
            logger.info(f"   📅 Período: 90 días")
            
            # Mostrar promedios por usuario
            logger.info("📈 Promedios diarios por usuario:")
            for user_id, stats in sorted(user_stats.items()):
                if stats['count'] > 0:
                    avg_pasos = int(stats['total_pasos'] / stats['count'])
                    avg_distancia = round(stats['total_distancia'] / stats['count'], 1)
                    avg_calorias = int(stats['total_calorias'] / stats['count'])
                    avg_minutos = int(stats['total_minutos'] / stats['count'])
                    avg_pisos = int(stats['total_pisos'] / stats['count'])
                    
                    logger.info(f"   Usuario {user_id}: {avg_pasos} pasos, {avg_distancia}km, "
                              f"{avg_calorias} cal, {avg_minutos}min, {avg_pisos} pisos")
                
        except Exception as e:
            logger.error(f"❌ Error durante el seeding de actividad física: {str(e)}")
            self.db.rollback()
            raise e

def main():
    """Función para ejecutar el seeder de forma independiente"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Seeder de Actividad Física')
    parser.add_argument('--clear', action='store_true', help='Limpiar datos existentes')
    args = parser.parse_args()
    
    try:
        with PhysicalActivitySeeder() as seeder:
            seeder.create_tables()
            seeder.run(
                clear_first=args.clear,
                table_names=['tbb_actividad_fisica'] if args.clear else None
            )
        logger.info("✅ Seeder de actividad física completado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()