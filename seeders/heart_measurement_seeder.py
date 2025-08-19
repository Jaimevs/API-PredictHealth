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
        
        # 🏥 PERFILES MÉDICOS REALISTAS Y CORREGIDOS
        self.perfiles_medicos = {
            'saludable': {
                'nombre': 'Persona Saludable',
                'probabilidad': 0.65,  # 65% de la población
                'descripcion': 'Valores dentro de rangos normales',
                'rangos': {
                    'frecuencia_cardiaca': (60, 100),      # Rango normal estándar
                    'presion_sistolica': (90, 120),        # Presión normal
                    'presion_diastolica': (60, 80),        # Presión normal
                    'saturacion_oxigeno': (96, 100),       # Saturación excelente
                    'temperatura': (36.1, 37.2),           # Temperatura normal
                    'nivel_estres': (0, 40),               # Estrés bajo-moderado (0-100 escala)
                    'variabilidad_ritmo': (30, 60)         # Buena variabilidad
                }
            },
            'regular': {
                'nombre': 'Persona con Riesgo Moderado',
                'probabilidad': 0.25,  # 25% de la población
                'descripcion': 'Valores alterados pero controlables',
                'rangos': {
                    'frecuencia_cardiaca': (65, 110),      # Ligeramente elevada
                    'presion_sistolica': (120, 139),       # Pre-hipertensión
                    'presion_diastolica': (80, 89),        # Pre-hipertensión
                    'saturacion_oxigeno': (94, 97),        # Saturación reducida
                    'temperatura': (36.0, 37.5),           # Temperatura normal-alta
                    'nivel_estres': (30, 70),              # Estrés moderado-alto
                    'variabilidad_ritmo': (20, 35)         # Variabilidad reducida
                }
            },
            'alto_riesgo': {
                'nombre': 'Persona con Alto Riesgo',
                'probabilidad': 0.10,  # 10% de la población
                'descripcion': 'Valores que requieren monitoreo médico',
                'rangos': {
                    'frecuencia_cardiaca': (70, 120),      # Más variable
                    'presion_sistolica': (140, 159),       # Hipertensión estadio 1
                    'presion_diastolica': (90, 99),        # Hipertensión estadio 1
                    'saturacion_oxigeno': (90, 95),        # Saturación baja
                    'temperatura': (36.0, 38.0),           # Más variable
                    'nivel_estres': (50, 90),              # Estrés alto
                    'variabilidad_ritmo': (15, 25)         # Variabilidad muy reducida
                }
            }
        }
        
        # 📊 Mediciones por día según perfil (más realistas)
        self.mediciones_por_perfil = {
            'saludable': (8, 15),      # Pocas mediciones diarias
            'regular': (12, 20),       # Mediciones moderadas
            'alto_riesgo': (15, 25)    # Más mediciones (monitoreo frecuente)
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
        # Probabilidades base
        prob_saludable = 0.65
        prob_regular = 0.25
        prob_alto_riesgo = 0.10
        
        # Ajustes por edad
        if edad < 25:
            prob_saludable = 0.80
            prob_regular = 0.18
            prob_alto_riesgo = 0.02
        elif edad < 40:
            prob_saludable = 0.75
            prob_regular = 0.22
            prob_alto_riesgo = 0.03
        elif edad < 55:
            prob_saludable = 0.60
            prob_regular = 0.30
            prob_alto_riesgo = 0.10
        elif edad < 70:
            prob_saludable = 0.45
            prob_regular = 0.40
            prob_alto_riesgo = 0.15
        else:  # >70
            prob_saludable = 0.30
            prob_regular = 0.50
            prob_alto_riesgo = 0.20
        
        # Ajustes por condiciones de salud
        condiciones_count = sum([
            condiciones_salud.get('fumador', False),
            condiciones_salud.get('diabetico', False),
            condiciones_salud.get('hipertenso', False),
            condiciones_salud.get('historial_cardiaco', False)
        ])
        
        if condiciones_count == 0:
            # Sin condiciones - más saludable
            prob_saludable = min(0.90, prob_saludable + 0.15)
            prob_regular = max(0.08, prob_regular - 0.10)
            prob_alto_riesgo = max(0.02, prob_alto_riesgo - 0.05)
        elif condiciones_count >= 2:
            # Múltiples condiciones - más riesgo
            prob_saludable = max(0.10, prob_saludable - 0.30)
            prob_regular = min(0.60, prob_regular + 0.15)
            prob_alto_riesgo = min(0.30, prob_alto_riesgo + 0.15)
        elif condiciones_salud.get('historial_cardiaco', False):
            # Historial cardíaco es crítico
            prob_saludable = max(0.20, prob_saludable - 0.25)
            prob_regular = min(0.60, prob_regular + 0.15)
            prob_alto_riesgo = min(0.20, prob_alto_riesgo + 0.10)
        
        # Normalizar probabilidades
        total = prob_saludable + prob_regular + prob_alto_riesgo
        prob_saludable /= total
        prob_regular /= total
        prob_alto_riesgo /= total
        
        # Seleccionar perfil
        rand = random.random()
        if rand < prob_saludable:
            return 'saludable'
        elif rand < prob_saludable + prob_regular:
            return 'regular'
        else:
            return 'alto_riesgo'
    
    def obtener_smartwatches_activos(self):
        """Obtener smartwatches activos con información del usuario"""
        print("🔍 Obteniendo smartwatches activos...")
        
        query = text("""
            SELECT 
                s.ID as smartwatch_id,
                s.Usuario_ID,
                s.Fecha_vinculacion,
                p.Fecha_Nacimiento,
                p.Genero,
                COALESCE(hp.Fumador, 0) as fumador,
                COALESCE(hp.Diabetico, 0) as diabetico,
                COALESCE(hp.Hipertenso, 0) as hipertenso,
                COALESCE(hp.Historial_cardiaco, 0) as historial_cardiaco,
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
                'fumador': bool(row[5]),
                'diabetico': bool(row[6]),
                'hipertenso': bool(row[7]),
                'historial_cardiaco': bool(row[8]),
                'activo': bool(row[9])
            }
            smartwatches_activos.append(smartwatch_data)
        
        print(f"✅ Smartwatches encontrados: {len(smartwatches_activos):,}")
        return smartwatches_activos
    
    def generar_frecuencia_cardiaca(self, perfil, hora, edad, genero, actividad_factor=1.0):
        """Generar frecuencia cardíaca realista"""
        rangos = self.perfiles_medicos[perfil]['rangos']
        fc_min, fc_max = rangos['frecuencia_cardiaca']
        
        # 🕐 Variación por hora del día
        if 22 <= hora or hora <= 5:
            # Sueño profundo - FC más baja
            factor_hora = 0.75
        elif 6 <= hora <= 8:
            # Despertar - FC gradualmente aumenta
            factor_hora = 0.85
        elif 9 <= hora <= 11 or 14 <= hora <= 17:
            # Horas activas - FC normal-alta
            factor_hora = 1.1
        elif 18 <= hora <= 21:
            # Tarde-noche - FC normal
            factor_hora = 1.0
        else:
            factor_hora = 1.0
        
        # 👥 Ajuste por género (mujeres FC ligeramente más alta)
        if genero == GenderEnum.F:
            fc_min += 2
            fc_max += 5
        
        # Ajuste por edad
        if edad > 65:
            fc_min += 3
            fc_max += 8
        elif edad > 50:
            fc_min += 1
            fc_max += 4
        elif edad < 30:
            fc_min -= 2
            fc_max -= 1
        
        # Calcular FC base
        fc_base = random.randint(int(fc_min * factor_hora), int(fc_max * factor_hora))
        
        # Aplicar factor de actividad y variación natural
        variacion = random.uniform(-5, 5)  # ±5 bpm de variación natural
        fc_final = int(fc_base * actividad_factor + variacion)
        
        # 🚨 Límites de seguridad médica
        return max(40, min(fc_final, 200))
    
    def generar_presion_arterial(self, perfil, edad):
        """Generar presión arterial realista"""
        rangos = self.perfiles_medicos[perfil]['rangos']
        
        # Presión sistólica
        sys_min, sys_max = rangos['presion_sistolica']
        sistolica = random.randint(sys_min, sys_max)
        
        #  Ajuste por edad (presión tiende a aumentar)
        if edad > 60:
            sistolica += random.randint(5, 15)
        elif edad > 45:
            sistolica += random.randint(2, 8)
        
        # Presión diastólica (siempre menor que sistólica)
        dia_min, dia_max = rangos['presion_diastolica']
        diastolica = random.randint(dia_min, min(dia_max, sistolica - 30))
        
        # Ajuste diastólica por edad
        if edad > 60:
            diastolica += random.randint(3, 8)
        elif edad > 45:
            diastolica += random.randint(1, 4)
        
        # Límites finales de seguridad
        sistolica = max(70, min(sistolica, 250))
        diastolica = max(40, min(diastolica, sistolica - 20))
        
        return sistolica, diastolica
    
    def generar_saturacion_oxigeno(self, perfil, hora, edad):
        """Generar saturación de oxígeno realista"""
        rangos = self.perfiles_medicos[perfil]['rangos']
        sat_min, sat_max = rangos['saturacion_oxigeno']
        
        # Base según perfil
        saturacion = random.uniform(sat_min, sat_max)
        
        # Variación leve durante el sueño
        if 22 <= hora or hora <= 6:
            saturacion -= random.uniform(0.2, 1.0)
        
        # Ajuste por edad
        if edad > 70:
            saturacion -= random.uniform(0.5, 2.0)
        elif edad > 50:
            saturacion -= random.uniform(0.2, 1.0)
        
        # Límites de seguridad
        return round(max(85.0, min(saturacion, 100.0)), 1)
    
    def generar_temperatura(self, perfil, hora):
        """Generar temperatura corporal realista"""
        rangos = self.perfiles_medicos[perfil]['rangos']
        temp_min, temp_max = rangos['temperatura']
        
        temperatura = random.uniform(temp_min, temp_max)
        
        # ritmo circadiano natural
        if 3 <= hora <= 6:
            temperatura -= 0.4  # Mínimo en madrugada
        elif 16 <= hora <= 19:
            temperatura += 0.3  # Máximo en tarde
        elif 20 <= hora <= 22:
            temperatura += 0.1  # Ligeramente alta en noche
        
        return round(max(35.0, min(temperatura, 42.0)), 1)
    
    def generar_nivel_estres(self, perfil, hora):
        """Generar nivel de estrés realista (0-100)"""
        rangos = self.perfiles_medicos[perfil]['rangos']
        estres_min, estres_max = rangos['nivel_estres']
        
        estres_base = random.randint(estres_min, estres_max)
        
        # Variación por hora (estrés laboral)
        if 8 <= hora <= 12 or 14 <= hora <= 18:
            # Horas laborales - más estrés
            estres_base += random.randint(0, 20)
        elif 22 <= hora or hora <= 6:
            # Horas de descanso - menos estrés
            estres_base -= random.randint(5, 20)
        elif 19 <= hora <= 21:
            # Tarde - estrés moderado
            estres_base += random.randint(-5, 10)
        
        return max(0, min(estres_base, 100))
    
    def generar_variabilidad_ritmo(self, perfil, edad):
        """Generar variabilidad del ritmo cardíaco"""
        rangos = self.perfiles_medicos[perfil]['rangos']
        var_min, var_max = rangos['variabilidad_ritmo']
        
        variabilidad = random.uniform(var_min, var_max)
        
        # Disminuye con la edad
        if edad > 70:
            variabilidad *= 0.7
        elif edad > 55:
            variabilidad *= 0.8
        elif edad > 40:
            variabilidad *= 0.9
        elif edad < 25:
            variabilidad *= 1.1
        
        return round(max(5.0, min(variabilidad, 200.0)), 2)
    
    def generar_mediciones_para_smartwatch(self, smartwatch_data, dias_historial=30):
        """Generar mediciones para un smartwatch específico"""
        mediciones = []
        
        # Calcular edad y condiciones
        edad = self.calcular_edad(smartwatch_data['fecha_nacimiento'])
        condiciones = {
            'fumador': smartwatch_data['fumador'],
            'diabetico': smartwatch_data['diabetico'],
            'hipertenso': smartwatch_data['hipertenso'],
            'historial_cardiaco': smartwatch_data['historial_cardiaco']
        }
        
        # Asignar perfil médico
        perfil_medico = self.asignar_perfil_medico(edad, condiciones)
        
        # Mediciones por día
        mediciones_min, mediciones_max = self.mediciones_por_perfil[perfil_medico]
        
        print(f"👤 Usuario {smartwatch_data['usuario_id']}: {self.perfiles_medicos[perfil_medico]['nombre']} "
              f"(Edad: {edad}, {mediciones_min}-{mediciones_max} mediciones/día)")
        
        # Período de generación
        fecha_inicio = max(
            smartwatch_data['fecha_vinculacion'].date(),
            (datetime.now() - timedelta(days=dias_historial)).date()
        )
        
        # Generar por cada día
        for dia in range((datetime.now().date() - fecha_inicio).days + 1):
            fecha_dia = fecha_inicio + timedelta(days=dia)
            
            if fecha_dia > datetime.now().date():
                break
            
            # Mediciones para este día
            num_mediciones = random.randint(mediciones_min, mediciones_max)
            horas_usadas = set()
            
            for _ in range(num_mediciones):
                # Evitar duplicados en la misma hora
                intentos = 0
                while intentos < 10:
                    hora = random.randint(6, 23)  # Horario despierto
                    if hora not in horas_usadas or len(horas_usadas) >= 18:
                        break
                    intentos += 1
                
                horas_usadas.add(hora)
                minuto = random.randint(0, 59)
                segundo = random.randint(0, 59)
                
                timestamp = datetime.combine(fecha_dia, datetime.min.time().replace(
                    hour=hora, minute=minuto, second=segundo
                ))
                
                # Generar mediciones según perfil
                frecuencia_cardiaca = self.generar_frecuencia_cardiaca(
                    perfil_medico, hora, edad, smartwatch_data['genero']
                )
                
                nivel_estres = self.generar_nivel_estres(perfil_medico, hora)
                
                # Probabilidades realistas de medición
                presion_sistolica = presion_diastolica = None
                if random.random() < 0.80:  # 80% tienen presión
                    presion_sistolica, presion_diastolica = self.generar_presion_arterial(perfil_medico, edad)
                
                saturacion_oxigeno = None
                if random.random() < 0.85:  # 85% tienen saturación
                    saturacion_oxigeno = self.generar_saturacion_oxigeno(perfil_medico, hora, edad)
                
                temperatura = None
                if random.random() < 0.70:  # 70% tienen temperatura
                    temperatura = self.generar_temperatura(perfil_medico, hora)
                
                variabilidad_ritmo = None
                if random.random() < 0.90:  # 90% tienen variabilidad
                    variabilidad_ritmo = self.generar_variabilidad_ritmo(perfil_medico, edad)
                
                # Crear medición
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
        """Generar mediciones para todos los smartwatches"""
        print(f"🔧 Generando mediciones para {len(smartwatches_activos):,} smartwatches...")
        print(f"📅 Historial: {dias_historial} días\n")
        
        todas_mediciones = []
        perfiles_asignados = {'saludable': 0, 'regular': 0, 'alto_riesgo': 0}
        
        for i, smartwatch_data in enumerate(smartwatches_activos):
            mediciones_smartwatch, perfil = self.generar_mediciones_para_smartwatch(
                smartwatch_data, dias_historial
            )
            
            todas_mediciones.extend(mediciones_smartwatch)
            perfiles_asignados[perfil] += 1
        
        print(f"\n✅ Generación completada: {len(todas_mediciones):,} mediciones")
        
        # Mostrar distribución de perfiles
        print(f"\n🏥 Distribución de perfiles médicos:")
        total_usuarios = sum(perfiles_asignados.values())
        for perfil, cantidad in perfiles_asignados.items():
            porcentaje = (cantidad / total_usuarios) * 100
            nombre = self.perfiles_medicos[perfil]['nombre']
            print(f"   • {nombre}: {cantidad} usuarios ({porcentaje:.1f}%)")
        
        return todas_mediciones
    
    def insertar_mediciones_bulk(self, mediciones_data, batch_size=1000):
        """Insertar mediciones usando bulk insert optimizado"""
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
                porcentaje = (mediciones_insertadas / total_mediciones) * 100
                
                print(f"📈 Progreso: {mediciones_insertadas:,}/{total_mediciones:,} ({porcentaje:.1f}%)")
                
            except Exception as e:
                logger.error(f"Error insertando lote: {e}")
                self.db.rollback()
                raise
        
        elapsed = time.time() - start_time
        print(f"✅ Inserción completada en {elapsed:.2f} segundos")
        
        return mediciones_insertadas
    
    def mostrar_estadisticas(self, mediciones_data):
        """Mostrar estadísticas de las mediciones generadas"""
        if not mediciones_data:
            return
        
        print(f"\n📈 ESTADÍSTICAS DE MEDICIONES GENERADAS:")
        
        total = len(mediciones_data)
        con_presion = sum(1 for m in mediciones_data if m['Presion_sistolica'] is not None)
        con_saturacion = sum(1 for m in mediciones_data if m['Saturacion_oxigeno'] is not None)
        con_temperatura = sum(1 for m in mediciones_data if m['Temperatura'] is not None)
        con_variabilidad = sum(1 for m in mediciones_data if m['Variabilidad_ritmo'] is not None)
        
        print(f"💓 Total mediciones: {total:,}")
        print(f"📊 Completitud:")
        print(f"   • Frecuencia cardíaca: 100.0%")
        print(f"   • Presión arterial: {(con_presion/total)*100:.1f}%")
        print(f"   • Saturación O2: {(con_saturacion/total)*100:.1f}%")
        print(f"   • Temperatura: {(con_temperatura/total)*100:.1f}%")
        print(f"   • Variabilidad: {(con_variabilidad/total)*100:.1f}%")
        print(f"   • Nivel estrés: 100.0%")
        
        # Rangos generados
        frecuencias = [m['Frecuencia_cardiaca'] for m in mediciones_data]
        niveles_estres = [m['Nivel_estres'] for m in mediciones_data]
        
        print(f"\n📈 Rangos generados:")
        print(f"   • Frecuencia cardíaca: {min(frecuencias)}-{max(frecuencias)} bpm")
        print(f"   • Nivel estrés: {min(niveles_estres)}-{max(niveles_estres)}%")
        
        if con_presion > 0:
            presiones_sys = [m['Presion_sistolica'] for m in mediciones_data if m['Presion_sistolica']]
            presiones_dia = [m['Presion_diastolica'] for m in mediciones_data if m['Presion_diastolica']]
            print(f"   • Presión sistólica: {min(presiones_sys)}-{max(presiones_sys)} mmHg")
            print(f"   • Presión diastólica: {min(presiones_dia)}-{max(presiones_dia)} mmHg")
    
    def seed(self, dias_historial=30):
        """Ejecutar seeding de mediciones cardíacas corregidas"""
        logger.info("Iniciando seeding de mediciones cardíacas corregidas...")
        print(f"\n💓 SEEDING DE MEDICIONES CARDÍACAS CORREGIDAS")
        print("=" * 60)
        
        start_total = time.time()
        
        # 1. Obtener smartwatches
        smartwatches_activos = self.obtener_smartwatches_activos()
        
        if not smartwatches_activos:
            print("❌ No hay smartwatches disponibles.")
            return
        
        # 2. Mostrar perfiles médicos
        print(f"\n🏥 PERFILES MÉDICOS REALISTAS:")
        for perfil_key, perfil_data in self.perfiles_medicos.items():
            print(f"   • {perfil_data['nombre']}: {perfil_data['descripcion']} ({perfil_data['probabilidad']*100:.0f}%)")
        
        # 3. Generar mediciones
        mediciones_data = self.generar_mediciones_batch(smartwatches_activos, dias_historial)
        
        # 4. Mostrar estadísticas
        self.mostrar_estadisticas(mediciones_data)
        
        # 5. Insertar en base de datos
        mediciones_creadas = self.insertar_mediciones_bulk(mediciones_data)
        
        # 6. Resumen final
        total_elapsed = time.time() - start_total
        
        print(f"\n🎉 SEEDING COMPLETADO")
        print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos")
        print(f"📊 Mediciones creadas: {mediciones_creadas:,}")
        print(f"👥 Usuarios procesados: {len(smartwatches_activos):,}")
        print(f"📅 Período: {dias_historial} días")
        
        if len(smartwatches_activos) > 0:
            promedio = mediciones_creadas / len(smartwatches_activos)
            print(f"📈 Promedio por usuario: {promedio:.1f} mediciones")
    
    def run(self, clear_first=False, table_names=None):
        """Ejecutar el seeder corregido"""
        try:
            if clear_first and table_names:
                logger.info("🗑️ Limpiando datos existentes...")
                self.clear_tables(table_names)
            
            self.seed(dias_historial=30)
                
        except Exception as e:
            logger.error(f"❌ Error durante el seeding: {str(e)}")
            self.db.rollback()
            raise e

if __name__ == "__main__":
    try:
        with HeartMeasurementSeeder() as seeder:
            # Limpiar datos existentes si es necesario
            seeder.run(clear_first=True, table_names=['tbb_mediciones_cardiacas'])
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Seeder finalizado")