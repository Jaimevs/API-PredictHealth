from .base_seeder import BaseSeeder
from models.heart_measurement import HeartMeasurement
from models.smartwatch import Smartwatch
from models.user import User
from models.person import Person, GenderEnum
from models.health_profile import HealthProfile
import logging
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text

logger = logging.getLogger(__name__)

class HeartMeasurementSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Rangos normales de mediciones por edad y género
        self.rangos_normales = {
            'frecuencia_cardiaca': {
                'joven': (60, 100),     # 18-40 años
                'adulto': (65, 105),    # 40-65 años
                'mayor': (70, 110)      # 65+ años
            },
            'presion_sistolica': {
                'normal': (90, 120),
                'elevada': (120, 129),
                'alta': (130, 180)
            },
            'presion_diastolica': {
                'normal': (60, 80),
                'elevada': (80, 85),
                'alta': (85, 120)
            },
            'saturacion_oxigeno': (95.0, 100.0),
            'temperatura': (36.0, 37.5),
            'nivel_estres': (0, 100),
            'variabilidad_ritmo': (20.0, 50.0)
        }
        
        # Número de mediciones por smartwatch (por día)
        self.mediciones_por_dia = {
            'minimo': 10,    # Usuarios poco activos
            'promedio': 24,  # Una cada hora
            'maximo': 48     # Usuarios muy activos
        }
        
        # Patrones de medición durante el día
        self.patrones_horarios = [
            (6, 0.8),   # 6 AM - menos mediciones (dormido)
            (8, 1.2),   # 8 AM - más mediciones (despertando)
            (12, 1.5),  # 12 PM - pico de mediciones (actividad)
            (15, 1.3),  # 3 PM - actividad moderada
            (18, 1.4),  # 6 PM - actividad vespertina
            (22, 1.0),  # 10 PM - mediciones normales
            (0, 0.6)    # Medianoche - menos mediciones
        ]
    
    def calcular_edad(self, fecha_nacimiento):
        """Calcular edad actual basada en fecha de nacimiento"""
        today = datetime.now().date()
        if isinstance(fecha_nacimiento, datetime):
            fecha_nacimiento = fecha_nacimiento.date()
        
        return today.year - fecha_nacimiento.year - (
            (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
    
    def obtener_smartwatches_activos(self):
        """Obtener smartwatches activos con información del usuario"""
        print("🔍 Obteniendo smartwatches activos...")
        start_time = time.time()
        
        query = text("""
            SELECT 
                s.ID as smartwatch_id,
                s.Usuario_ID,
                s.Fecha_vinculacion,
                p.Fecha_Nacimiento,
                p.Genero,
                hp.Fumador,
                hp.Diabetico,
                hp.Hipertenso,
                hp.Historial_cardiaco
            FROM tbb_smartwatches s
            INNER JOIN tbb_usuarios u ON s.Usuario_ID = u.ID
            INNER JOIN tbb_personas p ON u.Persona_Id = p.ID
            LEFT JOIN tbb_perfil_salud hp ON u.ID = hp.Usuario_ID
            WHERE s.Estatus = 1 
            AND s.Activo = 1
            AND u.Estatus = 1 
            AND p.Estatus = 1
        """)
        
        result = self.db.execute(query).fetchall()
        smartwatches_activos = [
            {
                'smartwatch_id': row[0],
                'usuario_id': row[1],
                'fecha_vinculacion': row[2],
                'fecha_nacimiento': row[3],
                'genero': GenderEnum(row[4]) if row[4] else GenderEnum.M,
                'fumador': row[5] or False,
                'diabetico': row[6] or False,
                'hipertenso': row[7] or False,
                'historial_cardiaco': row[8] or False
            }
            for row in result
        ]
        
        elapsed = time.time() - start_time
        print(f"✅ Consulta completada en {elapsed:.2f} segundos")
        print(f"📊 Smartwatches activos encontrados: {len(smartwatches_activos):,}")
        
        return smartwatches_activos
    
    def generar_frecuencia_cardiaca(self, edad, genero, condiciones, hora, nivel_estres):
        """Generar frecuencia cardíaca realista"""
        # Determinar rango base por edad
        if edad < 40:
            base_min, base_max = self.rangos_normales['frecuencia_cardiaca']['joven']
        elif edad < 65:
            base_min, base_max = self.rangos_normales['frecuencia_cardiaca']['adulto']
        else:
            base_min, base_max = self.rangos_normales['frecuencia_cardiaca']['mayor']
        
        # Ajustes por género (las mujeres tienden a tener FC ligeramente más alta)
        if genero == GenderEnum.M:
            base_min += 5
            base_max += 5
        
        # Ajustes por condiciones de salud
        if condiciones['fumador']:
            base_min += 10
            base_max += 15
        if condiciones['diabetico']:
            base_min += 5
            base_max += 10
        if condiciones['hipertenso']:
            base_min += 8
            base_max += 12
        if condiciones['historial_cardiaco']:
            base_min += 15
            base_max += 20
        
        # Ajustes por hora del día
        if 6 <= hora <= 9:
            factor = 1.1  # Mañana - ligeramente elevada
        elif 10 <= hora <= 17:
            factor = 1.0  # Día - normal
        elif 18 <= hora <= 22:
            factor = 0.95  # Tarde - ligeramente baja
        else:
            factor = 0.8   # Noche - baja (reposo)
        
        # Ajuste por nivel de estrés
        stress_factor = 1 + (nivel_estres / 200)  # Max +50% por estrés máximo
        
        # Calcular rango final
        fc_min = int((base_min * factor * stress_factor))
        fc_max = int((base_max * factor * stress_factor))
        
        # Asegurar límites razonables
        fc_min = max(fc_min, 40)
        fc_max = min(fc_max, 200)
        
        return random.randint(fc_min, fc_max)
    
    def generar_presion_arterial(self, edad, condiciones):
        """Generar presión arterial sistólica y diastólica"""
        # Determinar si es hipertenso o tiene factores de riesgo
        es_hipertenso = condiciones['hipertenso']
        factores_riesgo = sum([
            condiciones['diabetico'],
            condiciones['fumador'],
            condiciones['historial_cardiaco'],
            edad > 50
        ])
        
        if es_hipertenso or factores_riesgo >= 2:
            # Presión alta
            sistolica_min, sistolica_max = self.rangos_normales['presion_sistolica']['alta']
            diastolica_min, diastolica_max = self.rangos_normales['presion_diastolica']['alta']
        elif factores_riesgo == 1 or edad > 40:
            # Presión elevada
            sistolica_min, sistolica_max = self.rangos_normales['presion_sistolica']['elevada']
            diastolica_min, diastolica_max = self.rangos_normales['presion_diastolica']['elevada']
        else:
            # Presión normal
            sistolica_min, sistolica_max = self.rangos_normales['presion_sistolica']['normal']
            diastolica_min, diastolica_max = self.rangos_normales['presion_diastolica']['normal']
        
        sistolica = random.randint(sistolica_min, sistolica_max)
        diastolica = random.randint(diastolica_min, diastolica_max)
        
        # Asegurar que la diastólica no sea mayor que la sistólica
        if diastolica >= sistolica:
            diastolica = sistolica - random.randint(20, 40)
            diastolica = max(diastolica, 50)  # Mínimo absoluto
        
        return sistolica, diastolica
    
    def generar_saturacion_oxigeno(self, condiciones, edad):
        """Generar saturación de oxígeno"""
        min_sat, max_sat = self.rangos_normales['saturacion_oxigeno']
        
        # Ajustes por condiciones
        if condiciones['fumador']:
            min_sat -= 3
            max_sat -= 1
        if condiciones['historial_cardiaco']:
            min_sat -= 2
            max_sat -= 1
        if edad > 70:
            min_sat -= 1
        
        # Asegurar límites
        min_sat = max(min_sat, 85.0)
        max_sat = min(max_sat, 100.0)
        
        return round(random.uniform(min_sat, max_sat), 1)
    
    def generar_temperatura(self):
        """Generar temperatura corporal"""
        min_temp, max_temp = self.rangos_normales['temperatura']
        return round(random.uniform(min_temp, max_temp), 1)
    
    def generar_nivel_estres(self, hora, condiciones):
        """Generar nivel de estrés (0-100)"""
        # Base por hora del día
        if 6 <= hora <= 9:
            base = random.randint(20, 40)  # Mañana - estrés moderado
        elif 10 <= hora <= 17:
            base = random.randint(30, 60)  # Trabajo - más estrés
        elif 18 <= hora <= 22:
            base = random.randint(15, 35)  # Tarde - relajándose
        else:
            base = random.randint(5, 20)   # Noche - muy bajo
        
        # Ajustes por condiciones
        if condiciones['fumador']:
            base += random.randint(10, 20)
        if condiciones['hipertenso']:
            base += random.randint(5, 15)
        if condiciones['diabetico']:
            base += random.randint(5, 10)
        
        return min(base, 100)
    
    def generar_variabilidad_ritmo(self, edad, condiciones):
        """Generar variabilidad del ritmo cardíaco"""
        min_var, max_var = self.rangos_normales['variabilidad_ritmo']
        
        # La variabilidad disminuye con la edad
        if edad > 60:
            min_var -= 10
            max_var -= 10
        elif edad > 40:
            min_var -= 5
            max_var -= 5
        
        # Condiciones que afectan la variabilidad
        if condiciones['historial_cardiaco']:
            min_var -= 8
            max_var -= 8
        if condiciones['diabetico']:
            min_var -= 5
            max_var -= 5
        
        # Asegurar límites
        min_var = max(min_var, 5.0)
        max_var = max(max_var, min_var + 5)
        
        return round(random.uniform(min_var, max_var), 2)
    
    def generar_mediciones_para_smartwatch(self, smartwatch_data, dias_historial=30):
        """Generar mediciones para un smartwatch específico"""
        mediciones = []
        
        # Calcular edad y preparar condiciones
        edad = self.calcular_edad(smartwatch_data['fecha_nacimiento'])
        condiciones = {
            'fumador': smartwatch_data['fumador'],
            'diabetico': smartwatch_data['diabetico'],
            'hipertenso': smartwatch_data['hipertenso'],
            'historial_cardiaco': smartwatch_data['historial_cardiaco']
        }
        
        # Determinar cuántas mediciones por día (basado en perfil del usuario)
        if edad < 30:
            mediciones_diarias = random.randint(20, 48)  # Jóvenes más activos
        elif edad < 50:
            mediciones_diarias = random.randint(15, 30)  # Adultos moderados
        else:
            mediciones_diarias = random.randint(10, 20)  # Mayores menos activos
        
        # Generar mediciones para cada día
        fecha_inicio = max(
            smartwatch_data['fecha_vinculacion'].date(),
            (datetime.now() - timedelta(days=dias_historial)).date()
        )
        
        for dia in range((datetime.now().date() - fecha_inicio).days + 1):
            fecha_dia = fecha_inicio + timedelta(days=dia)
            
            # Evitar fechas futuras
            if fecha_dia > datetime.now().date():
                break
            
            # Número de mediciones para este día (con algo de variación)
            num_mediciones = max(1, mediciones_diarias + random.randint(-5, 5))
            
            # Generar mediciones distribuidas a lo largo del día
            for _ in range(num_mediciones):
                # Hora aleatoria del día
                hora = random.randint(0, 23)
                minuto = random.randint(0, 59)
                segundo = random.randint(0, 59)
                
                timestamp = datetime.combine(fecha_dia, datetime.min.time().replace(
                    hour=hora, minute=minuto, second=segundo
                ))
                
                # Generar nivel de estrés primero (afecta otras mediciones)
                nivel_estres = self.generar_nivel_estres(hora, condiciones)
                
                # Generar todas las mediciones
                frecuencia_cardiaca = self.generar_frecuencia_cardiaca(
                    edad, smartwatch_data['genero'], condiciones, hora, nivel_estres
                )
                
                # No todas las mediciones incluyen presión arterial (solo algunos smartwatches)
                if random.random() < 0.7:  # 70% incluyen presión
                    presion_sistolica, presion_diastolica = self.generar_presion_arterial(edad, condiciones)
                else:
                    presion_sistolica = presion_diastolica = None
                
                # Saturación de oxígeno (80% de las mediciones)
                saturacion_oxigeno = self.generar_saturacion_oxigeno(condiciones, edad) if random.random() < 0.8 else None
                
                # Temperatura (60% de las mediciones)
                temperatura = self.generar_temperatura() if random.random() < 0.6 else None
                
                # Variabilidad del ritmo (90% de las mediciones)
                variabilidad_ritmo = self.generar_variabilidad_ritmo(edad, condiciones) if random.random() < 0.9 else None
                
                medicion = {
                    'Usuario_ID': smartwatch_data['usuario_id'],
                    'Smartwatch_ID': smartwatch_data['smartwatch_id'],
                    'Timestamp_medicion': timestamp,
                    'Frecuencia_cardiaca': frecuencia_cardiaca,
                    'Presion_sistolica': presion_sistolica,
                    'Presion_diastolica': presion_diastolica,
                    'Saturacion_oxigeno': Decimal(str(saturacion_oxigeno)) if saturacion_oxigeno else None,
                    'Temperatura': Decimal(str(temperatura)) if temperatura else None,
                    'Nivel_estres': nivel_estres,
                    'Variabilidad_ritmo': Decimal(str(variabilidad_ritmo)) if variabilidad_ritmo else None,
                    'Estatus': True,
                    'Fecha_Registro': datetime.now()
                }
                
                mediciones.append(medicion)
        
        return mediciones
    
    def generar_mediciones_batch(self, smartwatches_activos, dias_historial=30):
        """Generar mediciones cardíacas para todos los smartwatches"""
        print(f"🔧 Generando mediciones cardíacas para {len(smartwatches_activos):,} smartwatches...")
        print(f"📅 Historial: {dias_historial} días")
        start_time = time.time()
        
        todas_mediciones = []
        total_mediciones = 0
        
        for i, smartwatch_data in enumerate(smartwatches_activos):
            mediciones_smartwatch = self.generar_mediciones_para_smartwatch(
                smartwatch_data, dias_historial
            )
            
            todas_mediciones.extend(mediciones_smartwatch)
            total_mediciones += len(mediciones_smartwatch)
            
            # Mostrar progreso cada 100 smartwatches
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                promedio_mediciones = total_mediciones / (i + 1)
                
                print(f"📈 Procesados: {i + 1:,}/{len(smartwatches_activos):,} smartwatches "
                      f"- {total_mediciones:,} mediciones ({promedio_mediciones:.1f} prom/smartwatch) "
                      f"- {rate:.1f} smartwatches/seg")
        
        elapsed = time.time() - start_time
        promedio_final = total_mediciones / len(smartwatches_activos) if smartwatches_activos else 0
        
        print(f"✅ Generación completada en {elapsed:.2f} segundos")
        print(f"📊 Total de mediciones generadas: {total_mediciones:,}")
        print(f"📊 Promedio por smartwatch: {promedio_final:.1f} mediciones")
        
        return todas_mediciones
    
    def insertar_mediciones_bulk(self, mediciones_data, batch_size=5000):
        """Insertar mediciones usando bulk insert"""
        total_mediciones = len(mediciones_data)
        if total_mediciones == 0:
            print("💓 No hay mediciones para insertar.")
            return 0
        
        print(f"💾 Insertando {total_mediciones:,} mediciones en lotes de {batch_size:,}...")
        
        start_time = time.time()
        mediciones_insertadas = 0
        
        for i in range(0, total_mediciones, batch_size):
            batch = mediciones_data[i:i + batch_size]
            
            try:
                self.db.bulk_insert_mappings(HeartMeasurement, batch)
                self.db.commit()
                
                mediciones_insertadas += len(batch)
                
                # Mostrar progreso
                elapsed = time.time() - start_time
                if elapsed > 0:
                    rate = mediciones_insertadas / elapsed
                    porcentaje = (mediciones_insertadas / total_mediciones) * 100
                    
                    print(f"📈 Insertadas: {mediciones_insertadas:,}/{total_mediciones:,} "
                          f"({porcentaje:.1f}%) - {rate:.0f} mediciones/seg")
                
            except Exception as e:
                logger.error(f"Error insertando lote {i//batch_size + 1}: {e}")
                self.db.rollback()
                raise
        
        elapsed = time.time() - start_time
        final_rate = mediciones_insertadas / elapsed if elapsed > 0 else 0
        
        print(f"✅ Inserción completada en {elapsed:.2f} segundos ({final_rate:.0f} mediciones/seg)")
        
        return mediciones_insertadas
    
    def mostrar_estadisticas(self, mediciones_data):
        """Mostrar estadísticas de las mediciones generadas"""
        if not mediciones_data:
            print("📊 No hay datos para mostrar estadísticas.")
            return
        
        print(f"\n📈 Estadísticas de mediciones cardíacas generadas:")
        
        # Estadísticas básicas
        total = len(mediciones_data)
        con_presion = sum(1 for m in mediciones_data if m['Presion_sistolica'] is not None)
        con_saturacion = sum(1 for m in mediciones_data if m['Saturacion_oxigeno'] is not None)
        con_temperatura = sum(1 for m in mediciones_data if m['Temperatura'] is not None)
        con_variabilidad = sum(1 for m in mediciones_data if m['Variabilidad_ritmo'] is not None)
        
        print(f"💓 Total de mediciones: {total:,}")
        print(f"\n📊 Completitud de datos:")
        print(f"   • Frecuencia cardíaca: {total:,} (100.0%)")
        print(f"   • Presión arterial: {con_presion:,} ({(con_presion/total)*100:.1f}%)")
        print(f"   • Saturación O2: {con_saturacion:,} ({(con_saturacion/total)*100:.1f}%)")
        print(f"   • Temperatura: {con_temperatura:,} ({(con_temperatura/total)*100:.1f}%)")
        print(f"   • Variabilidad ritmo: {con_variabilidad:,} ({(con_variabilidad/total)*100:.1f}%)")
        print(f"   • Nivel de estrés: {total:,} (100.0%)")
        
        # Rangos de valores
        frecuencias = [m['Frecuencia_cardiaca'] for m in mediciones_data]
        niveles_estres = [m['Nivel_estres'] for m in mediciones_data]
        
        print(f"\n📈 Rangos de valores:")
        print(f"   • Frecuencia cardíaca: {min(frecuencias)}-{max(frecuencias)} bpm")
        print(f"   • Nivel de estrés: {min(niveles_estres)}-{max(niveles_estres)}%")
        
        if con_presion > 0:
            presiones_sys = [m['Presion_sistolica'] for m in mediciones_data if m['Presion_sistolica']]
            presiones_dia = [m['Presion_diastolica'] for m in mediciones_data if m['Presion_diastolica']]
            print(f"   • Presión sistólica: {min(presiones_sys)}-{max(presiones_sys)} mmHg")
            print(f"   • Presión diastólica: {min(presiones_dia)}-{max(presiones_dia)} mmHg")
    
    def seed(self, dias_historial=30):
        """Seed para mediciones cardíacas basado en smartwatches activos"""
        logger.info("Iniciando seeding de mediciones cardíacas...")
        print(f"\n💓 Iniciando creación de mediciones cardíacas...")
        
        start_total = time.time()
        
        # 1. Obtener smartwatches activos
        smartwatches_activos = self.obtener_smartwatches_activos()
        
        if not smartwatches_activos:
            print("✅ No hay smartwatches activos. No hay mediciones que generar.")
            return
        
        # 2. Generar mediciones en memoria
        mediciones_data = self.generar_mediciones_batch(smartwatches_activos, dias_historial)
        
        # 3. Mostrar estadísticas antes de insertar
        self.mostrar_estadisticas(mediciones_data)
        
        # 4. Insertar usando bulk operations
        mediciones_creadas = self.insertar_mediciones_bulk(mediciones_data)
        
        # 5. Resumen final
        total_elapsed = time.time() - start_total
        total_rate = mediciones_creadas / total_elapsed if total_elapsed > 0 else 0
        
        print(f"\n🎉 ¡Seeding de mediciones cardíacas completado!")
        print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos")
        print(f"🚄 Velocidad promedio: {total_rate:.0f} mediciones/segundo")
        print(f"\n📊 Resumen final:")
        print(f"   • Mediciones creadas: {mediciones_creadas:,}")
        print(f"   • Smartwatches procesados: {len(smartwatches_activos):,}")
        if len(smartwatches_activos) > 0:
            promedio_por_smartwatch = mediciones_creadas / len(smartwatches_activos)
            print(f"   • Promedio por smartwatch: {promedio_por_smartwatch:.1f} mediciones")
        print(f"   • Período de datos: {dias_historial} días")
        
        logger.info(f"Seeding de mediciones cardíacas completado:")
        logger.info(f"- Tiempo total: {total_elapsed:.2f}s")
        logger.info(f"- Mediciones creadas: {mediciones_creadas}")
        logger.info(f"- Velocidad: {total_rate:.0f} mediciones/seg")

if __name__ == "__main__":
    try:
        with HeartMeasurementSeeder() as seeder:
            seeder.create_tables()
            # Generar 30 días de historial por defecto
            seeder.seed(dias_historial=30)
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")