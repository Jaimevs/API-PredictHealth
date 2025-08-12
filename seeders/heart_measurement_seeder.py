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
        
        # PERFILES MÉDICOS REALISTAS
        self.perfiles_medicos = {
            'saludable': {
                'nombre': 'Persona Saludable',
                'probabilidad': 0.60,  # 60% de la población
                'descripcion': 'Valores dentro de rangos normales',
                'rangos': {
                    'frecuencia_cardiaca': {
                        'reposo': (60, 80),      # FC en reposo normal
                        'activo': (80, 120),     # FC durante actividad
                        'variacion': 0.1         # ±10% de variación
                    },
                    'presion_sistolica': (90, 125),    # Presión normal
                    'presion_diastolica': (60, 85),    # Presión normal
                    'saturacion_oxigeno': (97, 100),   # Saturación excelente
                    'temperatura': (36.2, 37.0),       # Temperatura normal
                    'nivel_estres': (10, 40),          # Estrés bajo-moderado
                    'variabilidad_ritmo': (25, 50)     # Buena variabilidad
                }
            },
            'regular': {
                'nombre': 'Persona con Problemas Regulares',
                'probabilidad': 0.30,  # 30% de la población
                'descripcion': 'Valores alterados pero no críticos',
                'rangos': {
                    'frecuencia_cardiaca': {
                        'reposo': (80, 95),      # FC ligeramente elevada
                        'activo': (100, 140),    # FC más elevada en actividad
                        'variacion': 0.15        # ±15% de variación
                    },
                    'presion_sistolica': (125, 145),   # Pre-hipertensión/Hipertensión leve
                    'presion_diastolica': (85, 95),    # Presión diastólica elevada
                    'saturacion_oxigeno': (94, 97),    # Saturación reducida
                    'temperatura': (36.0, 37.3),       # Temperatura normal-alta
                    'nivel_estres': (35, 65),          # Estrés moderado-alto
                    'variabilidad_ritmo': (15, 30)     # Variabilidad reducida
                }
            },
            'grave': {
                'nombre': 'Persona con Problemas Graves',
                'probabilidad': 0.10,  # 10% de la población
                'descripcion': 'Valores patológicos que requieren atención médica',
                'rangos': {
                    'frecuencia_cardiaca': {
                        'reposo': (95, 110),     # FC elevada en reposo
                        'activo': (130, 160),    # FC muy elevada en actividad
                        'variacion': 0.20        # ±20% de variación
                    },
                    'presion_sistolica': (145, 170),   # Hipertensión moderada-severa
                    'presion_diastolica': (95, 110),   # Presión diastólica alta
                    'saturacion_oxigeno': (88, 94),    # Saturación baja
                    'temperatura': (36.0, 38.0),       # Temperatura variable
                    'nivel_estres': (55, 85),          # Estrés alto
                    'variabilidad_ritmo': (8, 20)      # Variabilidad muy reducida
                }
            }
        }
        
        # Número de mediciones por día según perfil
        self.mediciones_por_perfil = {
            'saludable': (15, 25),    # Mediciones moderadas
            'regular': (20, 35),      # Más mediciones (monitoreo)
            'grave': (25, 45)         # Muchas mediciones (seguimiento estricto)
        }
    
    def calcular_edad(self, fecha_nacimiento):
        """Calcular edad actual basada en fecha de nacimiento"""
        today = datetime.now().date()
        if isinstance(fecha_nacimiento, datetime):
            fecha_nacimiento = fecha_nacimiento.date()
        
        return today.year - fecha_nacimiento.year - (
            (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
    
    def asignar_perfil_medico(self, edad, condiciones_salud):
        """Asignar perfil médico basado en edad y condiciones de salud"""
        # Calcular probabilidades ajustadas por edad y condiciones
        prob_saludable = 0.60
        prob_regular = 0.30
        prob_grave = 0.10
        
        # Ajustes por edad
        if edad < 30:
            prob_saludable = 0.75
            prob_regular = 0.20
            prob_grave = 0.05
        elif edad > 60:
            prob_saludable = 0.40
            prob_regular = 0.45
            prob_grave = 0.15
        
        # Ajustes por condiciones de salud
        num_condiciones = sum([
            condiciones_salud.get('fumador', False),
            condiciones_salud.get('diabetico', False),
            condiciones_salud.get('hipertenso', False),
            condiciones_salud.get('historial_cardiaco', False)
        ])
        
        if num_condiciones == 0:
            # Sin condiciones - más probabilidad de ser saludable
            prob_saludable = 0.80
            prob_regular = 0.18
            prob_grave = 0.02
        elif num_condiciones >= 2:
            # Múltiples condiciones - más probabilidad de problemas
            prob_saludable = 0.20
            prob_regular = 0.50
            prob_grave = 0.30
        elif num_condiciones == 1:
            # Una condición - perfil intermedio
            if condiciones_salud.get('historial_cardiaco', False):
                # Historial cardíaco es más serio
                prob_saludable = 0.30
                prob_regular = 0.50
                prob_grave = 0.20
            else:
                prob_saludable = 0.45
                prob_regular = 0.45
                prob_grave = 0.10
        
        # Seleccionar perfil basado en probabilidades
        rand = random.random()
        if rand < prob_saludable:
            return 'saludable'
        elif rand < prob_saludable + prob_regular:
            return 'regular'
        else:
            return 'grave'
    
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
                hp.Historial_cardiaco,
                s.Activo
            FROM tbb_smartwatches s
            INNER JOIN tbb_usuarios u ON s.Usuario_ID = u.ID
            INNER JOIN tbb_personas p ON u.Persona_Id = p.ID
            LEFT JOIN tbb_perfil_salud hp ON u.ID = hp.Usuario_ID
            WHERE s.Estatus = 1 
            AND u.Estatus = 1 
            AND p.Estatus = 1
            ORDER BY s.Usuario_ID
        """)
        
        result = self.db.execute(query).fetchall()
        smartwatches_activos = []
        
        for row in result:
            smartwatch_data = {
                'smartwatch_id': row[0],
                'usuario_id': row[1],
                'fecha_vinculacion': row[2],
                'fecha_nacimiento': row[3],
                'genero': GenderEnum(row[4]) if row[4] else GenderEnum.M,
                'fumador': row[5] or False,
                'diabetico': row[6] or False,
                'hipertenso': row[7] or False,
                'historial_cardiaco': row[8] or False,
                'activo': row[9] or True
            }
            smartwatches_activos.append(smartwatch_data)
        
        elapsed = time.time() - start_time
        print(f"✅ Consulta completada en {elapsed:.2f} segundos")
        print(f"📊 Smartwatches encontrados: {len(smartwatches_activos):,}")
        
        return smartwatches_activos
    
    def generar_frecuencia_cardiaca(self, perfil, hora, edad, genero):
        """Generar frecuencia cardíaca realista según perfil médico"""
        perfil_data = self.perfiles_medicos[perfil]
        rangos = perfil_data['rangos']['frecuencia_cardiaca']
        
        # Determinar si es momento de reposo o actividad
        if 22 <= hora or hora <= 6:
            # Horas de sueño - FC más baja
            base_min, base_max = rangos['reposo']
            factor = 0.85  # 15% más baja durante el sueño
        elif 7 <= hora <= 9 or 17 <= hora <= 20:
            # Horas de actividad - FC más alta
            base_min, base_max = rangos['activo']
            factor = 1.0
        else:
            # Horas normales - entre reposo y actividad
            reposo_min, reposo_max = rangos['reposo']
            activo_min, activo_max = rangos['activo']
            base_min = (reposo_min + activo_min) // 2
            base_max = (reposo_max + activo_max) // 2
            factor = 1.0
        
        # Ajustes por género (mujeres tienden a tener FC ligeramente más alta)
        if genero == GenderEnum.M:
            base_min += 3
            base_max += 3
        
        # Ajustes por edad
        if edad > 65:
            base_min += 5
            base_max += 5
        elif edad < 30:
            base_min -= 3
            base_max -= 3
        
        # Calcular FC final
        fc_min = int(base_min * factor)
        fc_max = int(base_max * factor)
        
        # Aplicar variación del perfil
        variacion = rangos['variacion']
        fc_base = random.randint(fc_min, fc_max)
        variacion_valor = fc_base * variacion * random.uniform(-1, 1)
        fc_final = int(fc_base + variacion_valor)
        
        # Límites de seguridad
        return max(45, min(fc_final, 180))
    
    def generar_presion_arterial(self, perfil, edad):
        """Generar presión arterial según perfil médico"""
        perfil_data = self.perfiles_medicos[perfil]
        
        # Presión sistólica
        sys_min, sys_max = perfil_data['rangos']['presion_sistolica']
        sistolica = random.randint(sys_min, sys_max)
        
        # Presión diastólica
        dia_min, dia_max = perfil_data['rangos']['presion_diastolica']
        diastolica = random.randint(dia_min, dia_max)
        
        # Asegurar relación lógica entre sistólica y diastólica
        if diastolica >= sistolica:
            diastolica = sistolica - random.randint(30, 50)
        
        # Ajustes por edad
        if edad > 60:
            sistolica += random.randint(5, 15)
            diastolica += random.randint(3, 8)
        
        return max(80, sistolica), max(50, diastolica)
    
    def generar_saturacion_oxigeno(self, perfil, hora):
        """Generar saturación de oxígeno según perfil médico"""
        perfil_data = self.perfiles_medicos[perfil]
        sat_min, sat_max = perfil_data['rangos']['saturacion_oxigeno']
        
        saturacion_base = random.uniform(sat_min, sat_max)
        
        # Variación por hora (ligeramente más baja durante el sueño)
        if 22 <= hora or hora <= 6:
            saturacion_base -= random.uniform(0.5, 1.5)
        
        return round(max(85.0, min(saturacion_base, 100.0)), 1)
    
    def generar_temperatura(self, perfil, hora):
        """Generar temperatura corporal según perfil médico"""
        perfil_data = self.perfiles_medicos[perfil]
        temp_min, temp_max = perfil_data['rangos']['temperatura']
        
        temperatura_base = random.uniform(temp_min, temp_max)
        
        # Variación circadiana natural
        if 4 <= hora <= 6:
            temperatura_base -= 0.3  # Más baja en madrugada
        elif 14 <= hora <= 18:
            temperatura_base += 0.2  # Más alta en tarde
        
        return round(temperatura_base, 1)
    
    def generar_nivel_estres(self, perfil, hora):
        """Generar nivel de estrés según perfil médico"""
        perfil_data = self.perfiles_medicos[perfil]
        estres_min, estres_max = perfil_data['rangos']['nivel_estres']
        
        # Base según perfil
        estres_base = random.randint(estres_min, estres_max)
        
        # Variación por hora del día
        if 8 <= hora <= 11 or 13 <= hora <= 17:
            # Horas laborales - más estrés
            estres_base += random.randint(10, 20)
        elif 22 <= hora or hora <= 6:
            # Horas de descanso - menos estrés
            estres_base -= random.randint(10, 25)
        
        return max(0, min(estres_base, 100))
    
    def generar_variabilidad_ritmo(self, perfil, edad):
        """Generar variabilidad del ritmo cardíaco según perfil médico"""
        perfil_data = self.perfiles_medicos[perfil]
        var_min, var_max = perfil_data['rangos']['variabilidad_ritmo']
        
        variabilidad_base = random.uniform(var_min, var_max)
        
        # Ajuste por edad (disminuye con la edad)
        if edad > 60:
            variabilidad_base *= 0.8
        elif edad > 40:
            variabilidad_base *= 0.9
        elif edad < 30:
            variabilidad_base *= 1.1
        
        return round(max(5.0, variabilidad_base), 2)
    
    def generar_mediciones_para_smartwatch(self, smartwatch_data, dias_historial=30):
        """Generar mediciones para un smartwatch específico con perfil médico"""
        mediciones = []
        
        # Calcular edad y condiciones de salud
        edad = self.calcular_edad(smartwatch_data['fecha_nacimiento'])
        condiciones = {
            'fumador': smartwatch_data['fumador'],
            'diabetico': smartwatch_data['diabetico'],
            'hipertenso': smartwatch_data['hipertenso'],
            'historial_cardiaco': smartwatch_data['historial_cardiaco']
        }
        
        # Asignar perfil médico
        perfil_medico = self.asignar_perfil_medico(edad, condiciones)
        
        # Determinar mediciones por día según perfil
        mediciones_min, mediciones_max = self.mediciones_por_perfil[perfil_medico]
        
        # Ajustar por estado del smartwatch
        if not smartwatch_data['activo']:
            mediciones_min = int(mediciones_min * 0.4)
            mediciones_max = int(mediciones_max * 0.4)
        
        print(f"👤 Usuario {smartwatch_data['usuario_id']}: {self.perfiles_medicos[perfil_medico]['nombre']} "
              f"(Edad: {edad}, Mediciones: {mediciones_min}-{mediciones_max}/día)")
        
        # Generar mediciones para cada día
        fecha_inicio = max(
            smartwatch_data['fecha_vinculacion'].date(),
            (datetime.now() - timedelta(days=dias_historial)).date()
        )
        
        for dia in range((datetime.now().date() - fecha_inicio).days + 1):
            fecha_dia = fecha_inicio + timedelta(days=dia)
            
            if fecha_dia > datetime.now().date():
                break
            
            # Número de mediciones para este día
            num_mediciones = random.randint(mediciones_min, mediciones_max)
            
            for _ in range(num_mediciones):
                # Hora aleatoria del día
                hora = random.randint(0, 23)
                minuto = random.randint(0, 59)
                segundo = random.randint(0, 59)
                
                timestamp = datetime.combine(fecha_dia, datetime.min.time().replace(
                    hour=hora, minute=minuto, second=segundo
                ))
                
                # Generar todas las mediciones según el perfil médico
                frecuencia_cardiaca = self.generar_frecuencia_cardiaca(
                    perfil_medico, hora, edad, smartwatch_data['genero']
                )
                
                nivel_estres = self.generar_nivel_estres(perfil_medico, hora)
                
                # Presión arterial (85% de las mediciones)
                if random.random() < 0.85:
                    presion_sistolica, presion_diastolica = self.generar_presion_arterial(perfil_medico, edad)
                else:
                    presion_sistolica = presion_diastolica = None
                
                # Saturación de oxígeno (90% de las mediciones)
                saturacion_oxigeno = self.generar_saturacion_oxigeno(perfil_medico, hora) if random.random() < 0.90 else None
                
                # Temperatura (75% de las mediciones)
                temperatura = self.generar_temperatura(perfil_medico, hora) if random.random() < 0.75 else None
                
                # Variabilidad del ritmo (95% de las mediciones)
                variabilidad_ritmo = self.generar_variabilidad_ritmo(perfil_medico, edad) if random.random() < 0.95 else None
                
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
        
        return mediciones, perfil_medico
    
    def generar_mediciones_batch(self, smartwatches_activos, dias_historial=30):
        """Generar mediciones cardíacas para todos los smartwatches"""
        print(f"🔧 Generando mediciones cardíacas para {len(smartwatches_activos):,} smartwatches...")
        print(f"📅 Historial: {dias_historial} días")
        print(f"🏥 Distribuyendo perfiles médicos realistas...\n")
        
        start_time = time.time()
        todas_mediciones = []
        total_mediciones = 0
        perfiles_asignados = {'saludable': 0, 'regular': 0, 'grave': 0}
        
        for i, smartwatch_data in enumerate(smartwatches_activos):
            mediciones_smartwatch, perfil = self.generar_mediciones_para_smartwatch(
                smartwatch_data, dias_historial
            )
            
            todas_mediciones.extend(mediciones_smartwatch)
            total_mediciones += len(mediciones_smartwatch)
            perfiles_asignados[perfil] += 1
            
            # Mostrar progreso
            if (i + 1) % 5 == 0 or len(smartwatches_activos) <= 10:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                promedio_mediciones = total_mediciones / (i + 1)
                
                print(f"📈 Procesados: {i + 1:,}/{len(smartwatches_activos):,} usuarios "
                      f"- {total_mediciones:,} mediciones ({promedio_mediciones:.0f} prom/usuario)")
        
        elapsed = time.time() - start_time
        promedio_final = total_mediciones / len(smartwatches_activos) if smartwatches_activos else 0
        
        print(f"\n✅ Generación completada en {elapsed:.2f} segundos")
        print(f"📊 Total de mediciones generadas: {total_mediciones:,}")
        print(f"📊 Promedio por usuario: {promedio_final:.0f} mediciones")
        
        # Mostrar distribución de perfiles
        print(f"\n🏥 Distribución de perfiles médicos:")
        total_usuarios = sum(perfiles_asignados.values())
        for perfil, cantidad in perfiles_asignados.items():
            porcentaje = (cantidad / total_usuarios) * 100
            nombre = self.perfiles_medicos[perfil]['nombre']
            print(f"   • {nombre}: {cantidad} usuarios ({porcentaje:.1f}%)")
        
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
        
        print(f"\n📈 Rangos de valores generados:")
        print(f"   • Frecuencia cardíaca: {min(frecuencias)}-{max(frecuencias)} bpm")
        print(f"   • Nivel de estrés: {min(niveles_estres)}-{max(niveles_estres)}%")
        
        if con_presion > 0:
            presiones_sys = [m['Presion_sistolica'] for m in mediciones_data if m['Presion_sistolica']]
            presiones_dia = [m['Presion_diastolica'] for m in mediciones_data if m['Presion_diastolica']]
            print(f"   • Presión sistólica: {min(presiones_sys)}-{max(presiones_sys)} mmHg")
            print(f"   • Presión diastólica: {min(presiones_dia)}-{max(presiones_dia)} mmHg")
        
        if con_saturacion > 0:
            saturaciones = [float(m['Saturacion_oxigeno']) for m in mediciones_data if m['Saturacion_oxigeno']]
            print(f"   • Saturación O2: {min(saturaciones):.1f}-{max(saturaciones):.1f}%")
        
        # Mostrar usuarios procesados
        usuarios_procesados = sorted(set(m['Usuario_ID'] for m in mediciones_data))
        print(f"\n👥 Usuarios con mediciones: {usuarios_procesados}")
    
    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        try:
            from config.database import engine
            HeartMeasurement.__table__.create(engine, checkfirst=True)
            logger.info("✅ Tabla de mediciones cardíacas verificada/creada")
        except Exception as e:
            logger.warning(f"⚠️ Error al crear tabla de mediciones cardíacas: {e}")
    
    def seed(self, dias_historial=30):
        """Seed para mediciones cardíacas con perfiles médicos realistas"""
        logger.info("Iniciando seeding de mediciones cardíacas con perfiles realistas...")
        print(f"\n💓 Iniciando creación de mediciones cardíacas con perfiles médicos realistas...")
        
        start_total = time.time()
        
        # 1. Obtener smartwatches
        smartwatches_activos = self.obtener_smartwatches_activos()
        
        if not smartwatches_activos:
            print("❌ No hay smartwatches disponibles. Verifique que:")
            print("   • Los usuarios tengan smartwatches asignados")
            print("   • Ejecute primero SmartwatchSeeder si es necesario")
            return
        
        # 2. Mostrar información de perfiles médicos
        print(f"\n🏥 PERFILES MÉDICOS DISPONIBLES:")
        for perfil_key, perfil_data in self.perfiles_medicos.items():
            print(f"   • {perfil_data['nombre']}: {perfil_data['descripcion']} ({perfil_data['probabilidad']*100:.0f}%)")
        
        # 3. Generar mediciones en memoria
        mediciones_data = self.generar_mediciones_batch(smartwatches_activos, dias_historial)
        
        # 4. Mostrar estadísticas antes de insertar
        self.mostrar_estadisticas(mediciones_data)
        
        # 5. Insertar usando bulk operations
        mediciones_creadas = self.insertar_mediciones_bulk(mediciones_data)
        
        # 6. Resumen final
        total_elapsed = time.time() - start_total
        total_rate = mediciones_creadas / total_elapsed if total_elapsed > 0 else 0
        
        usuarios_procesados = sorted(set(sw['usuario_id'] for sw in smartwatches_activos))
        
        print(f"\n🎉 ¡Seeding de mediciones cardíacas completado!")
        print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos")
        print(f"🚄 Velocidad promedio: {total_rate:.0f} mediciones/segundo")
        print(f"\n📊 Resumen final:")
        print(f"   • Mediciones creadas: {mediciones_creadas:,}")
        print(f"   • Usuarios procesados: {usuarios_procesados}")
        print(f"   • Smartwatches procesados: {len(smartwatches_activos):,}")
        print(f"   • Período de datos: {dias_historial} días")
        print(f"   • Perfiles médicos: 3 tipos (saludable, regular, grave)")
        
        if len(smartwatches_activos) > 0:
            promedio_por_smartwatch = mediciones_creadas / len(smartwatches_activos)
            print(f"   • Promedio por usuario: {promedio_por_smartwatch:.1f} mediciones")
        
        logger.info(f"Seeding de mediciones cardíacas completado:")
        logger.info(f"- Usuarios procesados: {usuarios_procesados}")
        logger.info(f"- Tiempo total: {total_elapsed:.2f}s")
        logger.info(f"- Mediciones creadas: {mediciones_creadas}")
        logger.info(f"- Velocidad: {total_rate:.0f} mediciones/seg")
    
    def run(self, clear_first=False, table_names=None):
        """Ejecutar el seeder de mediciones cardíacas"""
        try:
            if clear_first and table_names:
                logger.info("🗑️ Limpiando datos existentes de mediciones cardíacas...")
                self.clear_tables(table_names)
            
            logger.info("💓 Ejecutando seeder de mediciones cardíacas...")
            
            # Ejecutar el seed con parámetros por defecto
            self.seed(dias_historial=30)
                
        except Exception as e:
            logger.error(f"❌ Error durante el seeding de mediciones cardíacas: {str(e)}")
            self.db.rollback()
            raise e

if __name__ == "__main__":
    try:
        with HeartMeasurementSeeder() as seeder:
            seeder.create_tables()
            # Generar 30 días de historial con perfiles médicos realistas
            seeder.seed(dias_historial=30)
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")