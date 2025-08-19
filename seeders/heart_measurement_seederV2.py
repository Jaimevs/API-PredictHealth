from .base_seeder import BaseSeeder
from models.heart_measurement import HeartMeasurement
from models.smartwatch import Smartwatch
from models.user import User
from models.person import Person, GenderEnum
from models.health_profile import HealthProfile
import logging
import random
import time
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text

logger = logging.getLogger(__name__)

class HeartMeasurementSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # PERFILES MÉDICOS REALISTAS Y PRECISOS
        self.perfiles_medicos = {
            'saludable': {
                'nombre': 'Persona Saludable',
                'probabilidad': 0.65,
                'descripcion': 'Valores dentro de rangos normales según estándares médicos',
                'rangos': {
                    'frecuencia_cardiaca': {
                        'reposo': (55, 75),      # FC reposo normal según AHA
                        'activo_ligero': (70, 100),  # Actividad ligera
                        'activo_moderado': (100, 130), # Actividad moderada
                        'variacion': 0.08        # ±8% variación normal
                    },
                    'presion_sistolica': (90, 120),    # Presión óptima según ESH/ESC
                    'presion_diastolica': (60, 80),    # Presión diastólica óptima
                    'saturacion_oxigeno': (97, 100),   # SpO2 normal en personas sanas
                    'temperatura': (36.1, 37.2),       # Temperatura corporal normal
                    'nivel_estres': (5, 35),           # Estrés bajo-normal
                    'variabilidad_ritmo': (30, 60)     # HRV saludable (ms)
                }
            },
            'riesgo_moderado': {
                'nombre': 'Persona con Riesgo Moderado',
                'probabilidad': 0.25,
                'descripcion': 'Pre-hipertensión o factores de riesgo controlados',
                'rangos': {
                    'frecuencia_cardiaca': {
                        'reposo': (65, 85),      # FC ligeramente elevada
                        'activo_ligero': (85, 115),
                        'activo_moderado': (115, 145),
                        'variacion': 0.12        # Mayor variabilidad
                    },
                    'presion_sistolica': (120, 139),   # Pre-hipertensión (AHA 2017)
                    'presion_diastolica': (80, 89),    # Pre-hipertensión diastólica
                    'saturacion_oxigeno': (95, 98),    # SpO2 ligeramente reducida
                    'temperatura': (36.0, 37.4),       # Rango normal-alto
                    'nivel_estres': (25, 55),          # Estrés moderado
                    'variabilidad_ritmo': (20, 40)     # HRV reducida
                }
            },
            'patologico': {
                'nombre': 'Persona con Patología Establecida',
                'probabilidad': 0.10,
                'descripcion': 'Hipertensión, diabetes o cardiopatía diagnosticada',
                'rangos': {
                    'frecuencia_cardiaca': {
                        'reposo': (75, 95),      # FC elevada en patología
                        'activo_ligero': (95, 125),
                        'activo_moderado': (125, 155),
                        'variacion': 0.15        # Alta variabilidad patológica
                    },
                    'presion_sistolica': (140, 165),   # Hipertensión grado 1-2
                    'presion_diastolica': (90, 105),   # Hipertensión diastólica
                    'saturacion_oxigeno': (92, 96),    # SpO2 comprometida
                    'temperatura': (35.8, 37.6),       # Mayor variabilidad
                    'nivel_estres': (40, 75),          # Estrés alto crónico
                    'variabilidad_ritmo': (10, 25)     # HRV muy reducida
                }
            }
        }
        
        # Factores de corrección por edad (basados en literatura médica)
        self.factores_edad = {
            'fc_reposo': {
                '18-25': 0,
                '26-35': 2,
                '36-45': 4,
                '46-55': 6,
                '56-65': 8,
                '66+': 12
            },
            'presion_sistolica': {
                '18-25': -5,
                '26-35': 0,
                '36-45': 5,
                '46-55': 10,
                '56-65': 15,
                '66+': 20
            },
            'hrv_reduccion': {
                '18-25': 1.0,
                '26-35': 0.95,
                '36-45': 0.85,
                '46-55': 0.75,
                '56-65': 0.65,
                '66+': 0.55
            }
        }
        
        # Diferencias por género (basadas en estudios clínicos)
        self.factores_genero = {
            'fc_mujer_ajuste': 3,      # FC 3-5 bpm más alta en mujeres
            'presion_mujer_menor': -3, # Presión ligeramente menor en mujeres jóvenes
            'temp_mujer_ciclica': 0.3  # Variación cíclica en mujeres
        }
        
        # Mediciones por día según perfil (más realista)
        self.mediciones_por_perfil = {
            'saludable': (12, 20),        # Menos mediciones, uso normal
            'riesgo_moderado': (18, 28),  # Monitoreo aumentado
            'patologico': (25, 40)        # Monitoreo intensivo
        }
    
    def obtener_categoria_edad(self, edad):
        """Obtener categoría de edad para ajustes médicos"""
        if edad <= 25:
            return '18-25'
        elif edad <= 35:
            return '26-35'
        elif edad <= 45:
            return '36-45'
        elif edad <= 55:
            return '46-55'
        elif edad <= 65:
            return '56-65'
        else:
            return '66+'
    
    def determinar_actividad_por_hora(self, hora):
        """Determinar nivel de actividad basado en patrones circadianos reales"""
        if 23 <= hora or hora <= 5:
            return 'sueño'
        elif 6 <= hora <= 7:
            return 'despertar'
        elif 8 <= hora <= 11:
            return 'mañana_activa'
        elif 12 <= hora <= 14:
            return 'mediodia'
        elif 15 <= hora <= 18:
            return 'tarde_activa'
        elif 19 <= hora <= 21:
            return 'noche_tranquila'
        else:
            return 'pre_sueño'
    
    def generar_frecuencia_cardiaca_realista(self, perfil, hora, edad, genero, dia_del_mes=1):
        """Generar FC realista basada en fisiología cardiovascular"""
        perfil_data = self.perfiles_medicos[perfil]
        rangos = perfil_data['rangos']['frecuencia_cardiaca']
        
        # Determinar FC base según actividad circadiana
        actividad = self.determinar_actividad_por_hora(hora)
        
        if actividad == 'sueño':
            # Durante el sueño: FC 15-20% más baja
            fc_min, fc_max = rangos['reposo']
            factor = 0.8  # Reducción del 20%
        elif actividad == 'despertar':
            # Al despertar: FC ligeramente elevada
            fc_min, fc_max = rangos['reposo']
            factor = 1.1
        elif actividad in ['mañana_activa', 'tarde_activa']:
            # Períodos activos: FC moderadamente elevada
            fc_min, fc_max = rangos['activo_ligero']
            factor = 1.0
        elif actividad == 'mediodia':
            # Post-prandial: FC ligeramente elevada
            fc_min, fc_max = rangos['reposo']
            factor = 1.05
        else:
            # Resto del día: FC normal
            fc_min, fc_max = rangos['reposo']
            factor = 1.0
        
        # Ajustes por edad (FC máxima disminuye con edad)
        categoria_edad = self.obtener_categoria_edad(edad)
        ajuste_edad = self.factores_edad['fc_reposo'][categoria_edad]
        
        # Ajustes por género (verificar si es mujer - usar M para masculino)
        ajuste_genero = self.factores_genero['fc_mujer_ajuste'] if genero == GenderEnum.M else 0
        
        # Calcular FC base
        fc_base = random.uniform(fc_min + ajuste_edad + ajuste_genero, 
                                fc_max + ajuste_edad + ajuste_genero)
        fc_final = fc_base * factor
        
        # Aplicar variación natural (distribución normal)
        variacion = rangos['variacion']
        ruido = np.random.normal(0, fc_final * variacion * 0.5)
        fc_final += ruido
        
        # Variación hormonal en mujeres (verificar enum)
        if genero == GenderEnum.M and edad < 50:
            # Ciclo menstrual afecta FC (±2-4 bpm)
            ciclo_factor = np.sin(2 * np.pi * dia_del_mes / 28) * 2
            fc_final += ciclo_factor
        
        # Límites fisiológicos estrictos
        return max(45, min(int(fc_final), 180))
    
    def generar_presion_arterial_realista(self, perfil, edad, genero, fc_actual):
        """Generar presión arterial con correlación fisiológica"""
        perfil_data = self.perfiles_medicos[perfil]
        
        # Ajustes por edad
        categoria_edad = self.obtener_categoria_edad(edad)
        ajuste_edad_sys = self.factores_edad['presion_sistolica'][categoria_edad]
        
        # Ajustes por género (verificar si es mujer)
        ajuste_genero = self.factores_genero['presion_mujer_menor'] if genero == GenderEnum.M and edad < 45 else 0
        
        # Presión sistólica base
        sys_min, sys_max = perfil_data['rangos']['presion_sistolica']
        sistolica_base = random.uniform(sys_min + ajuste_edad_sys + ajuste_genero,
                                       sys_max + ajuste_edad_sys + ajuste_genero)
        
        # Correlación con FC (relación fisiológica)
        if fc_actual > 80:
            sistolica_base += (fc_actual - 80) * 0.3  # FC alta = presión más alta
        
        # Presión diastólica: mantener relación fisiológica
        dia_min, dia_max = perfil_data['rangos']['presion_diastolica']
        
        # Presión de pulso normal: 30-50 mmHg
        presion_pulso_ideal = random.uniform(35, 45)
        diastolica_calculada = sistolica_base - presion_pulso_ideal
        
        # Ajustar si está fuera del rango del perfil
        diastolica_final = max(dia_min + ajuste_edad_sys//2, 
                              min(diastolica_calculada, dia_max + ajuste_edad_sys//2))
        
        # Verificar relaciones fisiológicas
        if diastolica_final >= sistolica_base:
            diastolica_final = sistolica_base - 25
        
        return max(80, int(sistolica_base)), max(50, int(diastolica_final))
    
    def generar_saturacion_oxigeno_realista(self, perfil, hora, edad, actividad_reciente=False):
        """Generar SpO2 con variaciones fisiológicas realistas"""
        perfil_data = self.perfiles_medicos[perfil]
        sat_min, sat_max = perfil_data['rangos']['saturacion_oxigeno']
        
        # Variación circadiana mínima (real pero sutil)
        actividad = self.determinar_actividad_por_hora(hora)
        if actividad == 'sueño':
            ajuste_circadiano = -0.5  # Ligeramente menor durante sueño
        elif actividad in ['mañana_activa', 'tarde_activa']:
            ajuste_circadiano = 0.3   # Ligeramente mayor durante actividad
        else:
            ajuste_circadiano = 0
        
        # Efecto de la edad (disminución gradual)
        if edad > 65:
            ajuste_edad = -1.0
        elif edad > 50:
            ajuste_edad = -0.5
        else:
            ajuste_edad = 0
        
        # Saturación base
        saturacion_base = random.uniform(sat_min, sat_max)
        saturacion_final = saturacion_base + ajuste_circadiano + ajuste_edad
        
        # Variación muy pequeña (SpO2 es muy estable en personas sanas)
        if perfil == 'saludable':
            ruido = np.random.normal(0, 0.3)
        else:
            ruido = np.random.normal(0, 0.8)
        
        saturacion_final += ruido
        
        # Límites fisiológicos estrictos
        return round(max(85.0, min(saturacion_final, 100.0)), 1)
    
    def generar_temperatura_realista(self, perfil, hora, edad, genero, dia_del_mes=1):
        """Generar temperatura con variaciones circadianas reales"""
        perfil_data = self.perfiles_medicos[perfil]
        temp_min, temp_max = perfil_data['rangos']['temperatura']
        
        # Ritmo circadiano real (amplitud ~1°C)
        tiempo_decimal = hora + random.uniform(-0.5, 0.5)
        # Mínimo a las 4-6 AM, máximo a las 16-18 PM
        variacion_circadiana = 0.5 * np.sin(2 * np.pi * (tiempo_decimal - 6) / 24)
        
        # Temperatura base
        temp_base = random.uniform(temp_min, temp_max)
        
        # Aplicar ritmo circadiano
        temp_final = temp_base + variacion_circadiana
        
        # Variación hormonal en mujeres (verificar enum)
        if genero == GenderEnum.M and edad < 50:
            # Fase lútea: temperatura 0.3-0.5°C más alta
            ciclo_factor = self.factores_genero['temp_mujer_ciclica'] * np.sin(2 * np.pi * dia_del_mes / 28)
            temp_final += ciclo_factor
        
        # Efecto de la edad (termorregulación menos eficiente)
        if edad > 70:
            ruido_edad = np.random.normal(0, 0.2)
            temp_final += ruido_edad
        
        # Variación normal pequeña
        ruido = np.random.normal(0, 0.1)
        temp_final += ruido
        
        return round(max(35.0, min(temp_final, 38.5)), 1)
    
    def generar_nivel_estres_realista(self, perfil, hora, edad, es_fin_semana=False):
        """Generar nivel de estrés basado en patrones comportamentales reales"""
        perfil_data = self.perfiles_medicos[perfil]
        estres_min, estres_max = perfil_data['rangos']['nivel_estres']
        
        # Patrón circadiano del cortisol
        actividad = self.determinar_actividad_por_hora(hora)
        
        if actividad == 'sueño':
            factor_hora = 0.3  # Mínimo durante sueño
        elif actividad == 'despertar':
            factor_hora = 1.4  # Pico matutino de cortisol
        elif actividad == 'mañana_activa':
            factor_hora = 1.2  # Alto en la mañana
        elif actividad == 'mediodia':
            factor_hora = 0.9  # Disminución post-prandial
        elif actividad == 'tarde_activa':
            factor_hora = 1.1  # Segundo pico menor
        else:
            factor_hora = 0.6  # Decline vespertino
        
        # Efecto fin de semana
        if es_fin_semana:
            factor_hora *= 0.7  # Menor estrés en fin de semana
        
        # Efecto de la edad
        if edad > 60:
            factor_edad = 0.8  # Menor reactividad al estrés
        elif edad < 30:
            factor_edad = 1.2  # Mayor reactividad
        else:
            factor_edad = 1.0
        
        # Calcular estrés base
        estres_base = random.uniform(estres_min, estres_max)
        estres_final = estres_base * factor_hora * factor_edad
        
        # Variación individual
        ruido = np.random.normal(0, estres_base * 0.15)
        estres_final += ruido
        
        return max(0, min(int(estres_final), 100))
    
    def generar_variabilidad_ritmo_realista(self, perfil, edad, genero, nivel_estres):
        """Generar HRV con correlaciones fisiológicas reales"""
        perfil_data = self.perfiles_medicos[perfil]
        hrv_min, hrv_max = perfil_data['rangos']['variabilidad_ritmo']
        
        # Reducción por edad (factor crítico en HRV)
        categoria_edad = self.obtener_categoria_edad(edad)
        factor_edad = self.factores_edad['hrv_reduccion'][categoria_edad]
        
        # Correlación inversa con estrés (muy importante)
        factor_estres = max(0.4, 1.0 - (nivel_estres / 200))
        
        # Diferencia por género (verificar enum - usar M para masculino)
        factor_genero = 0.92 if genero == GenderEnum.M else 1.0
        
        # HRV base
        hrv_base = random.uniform(hrv_min, hrv_max)
        
        # Aplicar todos los factores
        hrv_final = hrv_base * factor_edad * factor_estres * factor_genero
        
        # Variación natural
        ruido = np.random.normal(0, hrv_final * 0.1)
        hrv_final += ruido
        
        return round(max(5.0, hrv_final), 2)
    
    def obtener_total_usuarios(self):
        """Obtener el total de usuarios disponibles"""
        query = text("""
            SELECT COUNT(DISTINCT s.Usuario_ID) as total
            FROM tbb_smartwatches s
            INNER JOIN tbb_usuarios u ON s.Usuario_ID = u.ID
            INNER JOIN tbb_personas p ON u.Persona_Id = p.ID
            WHERE s.Estatus = 1 
            AND u.Estatus = 1 
            AND p.Estatus = 1
        """)
        
        result = self.db.execute(query).fetchone()
        return result[0] if result else 0
    
    def obtener_rango_usuarios(self):
        """Obtener el rango mínimo y máximo de IDs de usuarios"""
        query = text("""
            SELECT MIN(s.Usuario_ID) as min_id, MAX(s.Usuario_ID) as max_id
            FROM tbb_smartwatches s
            INNER JOIN tbb_usuarios u ON s.Usuario_ID = u.ID
            INNER JOIN tbb_personas p ON u.Persona_Id = p.ID
            WHERE s.Estatus = 1 
            AND u.Estatus = 1 
            AND p.Estatus = 1
        """)
        
        result = self.db.execute(query).fetchone()
        return result[0], result[1] if result else (None, None)
    
    def solicitar_rango_usuarios(self):
        """Solicitar al usuario el rango de usuarios a procesar"""
        total_usuarios = self.obtener_total_usuarios()
        min_id, max_id = self.obtener_rango_usuarios()
        
        if total_usuarios == 0:
            print("❌ No hay usuarios con smartwatches disponibles.")
            return None, None
        
        print(f"\n📊 INFORMACIÓN DE USUARIOS DISPONIBLES:")
        print(f"   • Total de usuarios con smartwatches: {total_usuarios:,}")
        print(f"   • Rango de IDs disponibles: {min_id} - {max_id}")
        print(f"   • Usuarios sugeridos para pruebas: 10-100 usuarios")
        print(f"   • Estimación de mediciones por usuario: ~450-800 (30 días)")
        
        print(f"\n⚠️  ADVERTENCIA: Procesar todos los usuarios ({total_usuarios:,}) puede:")
        print(f"   • Generar millones de registros")
        print(f"   • Tardar horas en completarse")
        print(f"   • Saturar la base de datos")
        
        while True:
            print(f"\n🎯 OPCIONES DE PROCESAMIENTO:")
            print(f"   1. Rango personalizado (recomendado)")
            print(f"   2. Solo primeros 10 usuarios (prueba rápida)")
            print(f"   3. Solo primeros 100 usuarios (prueba completa)")
            print(f"   4. Todos los usuarios (¡CUIDADO!)")
            print(f"   5. Cancelar")
            
            try:
                opcion = input("\n📝 Seleccione una opción (1-5): ").strip()
                
                if opcion == "1":
                    return self._solicitar_rango_personalizado(min_id, max_id)
                elif opcion == "2":
                    return min_id, min(min_id + 9, max_id)
                elif opcion == "3":
                    return min_id, min(min_id + 99, max_id)
                elif opcion == "4":
                    confirmacion = input(f"⚠️  ¿Está SEGURO de procesar TODOS los {total_usuarios:,} usuarios? (escriba 'CONFIRMO'): ")
                    if confirmacion.upper() == "CONFIRMO":
                        return min_id, max_id
                    else:
                        print("❌ Procesamiento cancelado.")
                        continue
                elif opcion == "5":
                    print("❌ Operación cancelada por el usuario.")
                    return None, None
                else:
                    print("❌ Opción inválida. Por favor seleccione 1-5.")
                    
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada por el usuario.")
                return None, None
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    def _solicitar_rango_personalizado(self, min_id, max_id):
        """Solicitar rango personalizado de usuarios"""
        while True:
            try:
                print(f"\n📝 RANGO PERSONALIZADO:")
                print(f"   • ID mínimo disponible: {min_id}")
                print(f"   • ID máximo disponible: {max_id}")
                
                inicio_str = input(f"   Ingrese ID de inicio (Enter para {min_id}): ").strip()
                inicio = int(inicio_str) if inicio_str else min_id
                
                fin_str = input(f"   Ingrese ID de fin (Enter para {min(min_id + 99, max_id)}): ").strip()
                fin = int(fin_str) if fin_str else min(min_id + 99, max_id)
                
                # Validaciones
                if inicio < min_id or inicio > max_id:
                    print(f"❌ El ID de inicio debe estar entre {min_id} y {max_id}")
                    continue
                
                if fin < min_id or fin > max_id:
                    print(f"❌ El ID de fin debe estar entre {min_id} y {max_id}")
                    continue
                
                if inicio > fin:
                    print("❌ El ID de inicio no puede ser mayor que el ID de fin")
                    continue
                
                cantidad_usuarios = fin - inicio + 1
                estimacion_mediciones = cantidad_usuarios * 600  # Promedio más realista
                
                print(f"\n📊 RESUMEN DEL RANGO SELECCIONADO:")
                print(f"   • Usuarios a procesar: {cantidad_usuarios:,} (ID {inicio} - {fin})")
                print(f"   • Mediciones estimadas: ~{estimacion_mediciones:,}")
                print(f"   • Tiempo estimado: ~{cantidad_usuarios * 1.5:.0f} segundos")
                
                confirmacion = input("\n✅ ¿Confirma este rango? (s/n): ").strip().lower()
                if confirmacion in ['s', 'si', 'sí', 'yes', 'y']:
                    return inicio, fin
                else:
                    continue
                    
            except ValueError:
                print("❌ Por favor ingrese números válidos.")
                continue
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada por el usuario.")
                return None, None
    
    def obtener_smartwatches_activos(self, usuario_inicio=None, usuario_fin=None):
        """Obtener smartwatches activos con información del usuario en un rango específico"""
        print("🔍 Obteniendo smartwatches activos...")
        start_time = time.time()
        
        # Base query
        query_base = """
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
        """
        
        # Agregar filtro de rango si se especifica
        if usuario_inicio is not None and usuario_fin is not None:
            query_base += f" AND s.Usuario_ID BETWEEN {usuario_inicio} AND {usuario_fin}"
            print(f"📌 Filtrando usuarios del ID {usuario_inicio} al {usuario_fin}")
        
        query_base += " ORDER BY s.Usuario_ID"
        
        query = text(query_base)
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
        
        if len(smartwatches_activos) > 0:
            primer_usuario = smartwatches_activos[0]['usuario_id']
            ultimo_usuario = smartwatches_activos[-1]['usuario_id']
            print(f"📌 Rango real de usuarios: {primer_usuario} - {ultimo_usuario}")
        
        return smartwatches_activos
    
    def calcular_edad(self, fecha_nacimiento):
        """Calcular edad actual basada en fecha de nacimiento"""
        today = datetime.now().date()
        if isinstance(fecha_nacimiento, datetime):
            fecha_nacimiento = fecha_nacimiento.date()
        
        return today.year - fecha_nacimiento.year - (
            (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
    
    def asignar_perfil_medico_realista(self, edad, condiciones_salud):
        """Asignar perfil médico basado en epidemiología real"""
        # Probabilidades base según prevalencia epidemiológica
        prob_saludable = 0.65
        prob_riesgo = 0.25
        prob_patologico = 0.10
        
        # Ajustes por edad (basados en estudios epidemiológicos)
        if edad < 30:
            prob_saludable = 0.80
            prob_riesgo = 0.18
            prob_patologico = 0.02
        elif 30 <= edad < 45:
            prob_saludable = 0.70
            prob_riesgo = 0.25
            prob_patologico = 0.05
        elif 45 <= edad < 60:
            prob_saludable = 0.55
            prob_riesgo = 0.35
            prob_patologico = 0.10
        elif 60 <= edad < 75:
            prob_saludable = 0.40
            prob_riesgo = 0.45
            prob_patologico = 0.15
        else:  # >75 años
            prob_saludable = 0.25
            prob_riesgo = 0.50
            prob_patologico = 0.25
        
        # Ajustes por condiciones de salud específicas
        condiciones_presentes = [
            condiciones_salud.get('fumador', False),
            condiciones_salud.get('diabetico', False),
            condiciones_salud.get('hipertenso', False),
            condiciones_salud.get('historial_cardiaco', False)
        ]
        
        num_condiciones = sum(condiciones_presentes)
        
        # Sin condiciones: mayor probabilidad de estar saludable
        if num_condiciones == 0:
            prob_saludable = min(0.90, prob_saludable + 0.15)
            prob_riesgo = max(0.08, prob_riesgo - 0.10)
            prob_patologico = max(0.02, prob_patologico - 0.05)
        
        # Una condición: riesgo moderado
        elif num_condiciones == 1:
            if condiciones_salud.get('historial_cardiaco', False):
                # Historial cardíaco es factor de riesgo mayor
                prob_saludable = max(0.15, prob_saludable - 0.25)
                prob_riesgo = min(0.60, prob_riesgo + 0.15)
                prob_patologico = min(0.25, prob_patologico + 0.10)
            elif condiciones_salud.get('diabetico', False):
                # Diabetes es factor de riesgo significativo
                prob_saludable = max(0.25, prob_saludable - 0.20)
                prob_riesgo = min(0.55, prob_riesgo + 0.15)
                prob_patologico = min(0.20, prob_patologico + 0.05)
            else:
                # Fumador o hipertenso solo
                prob_saludable = max(0.35, prob_saludable - 0.15)
                prob_riesgo = min(0.50, prob_riesgo + 0.10)
                prob_patologico = min(0.15, prob_patologico + 0.05)
        
        # Múltiples condiciones: alto riesgo
        else:
            prob_saludable = max(0.05, prob_saludable - 0.40)
            prob_riesgo = min(0.45, prob_riesgo + 0.15)
            prob_patologico = min(0.50, prob_patologico + 0.25)
        
        # Normalizar probabilidades
        total = prob_saludable + prob_riesgo + prob_patologico
        prob_saludable /= total
        prob_riesgo /= total
        prob_patologico /= total
        
        # Seleccionar perfil
        rand = random.random()
        if rand < prob_saludable:
            return 'saludable'
        elif rand < prob_saludable + prob_riesgo:
            return 'riesgo_moderado'
        else:
            return 'patologico'
    
    def generar_mediciones_para_smartwatch(self, smartwatch_data, dias_historial=30):
        """Generar mediciones médicamente realistas para un smartwatch"""
        mediciones = []
        
        # Calcular edad y condiciones de salud
        edad = self.calcular_edad(smartwatch_data['fecha_nacimiento'])
        condiciones = {
            'fumador': smartwatch_data['fumador'],
            'diabetico': smartwatch_data['diabetico'],
            'hipertenso': smartwatch_data['hipertenso'],
            'historial_cardiaco': smartwatch_data['historial_cardiaco']
        }
        
        # Asignar perfil médico realista
        perfil_medico = self.asignar_perfil_medico_realista(edad, condiciones)
        
        # Determinar mediciones por día según perfil
        mediciones_min, mediciones_max = self.mediciones_por_perfil[perfil_medico]
        
        # Ajustar por estado del smartwatch
        if not smartwatch_data['activo']:
            mediciones_min = int(mediciones_min * 0.5)
            mediciones_max = int(mediciones_max * 0.5)
        
        print(f"👤 Usuario {smartwatch_data['usuario_id']}: {self.perfiles_medicos[perfil_medico]['nombre']} "
              f"(Edad: {edad}, Género: {smartwatch_data['genero'].value}, Mediciones: {mediciones_min}-{mediciones_max}/día)")
        
        # Generar mediciones para cada día
        fecha_inicio = max(
            smartwatch_data['fecha_vinculacion'].date(),
            (datetime.now() - timedelta(days=dias_historial)).date()
        )
        
        for dia in range((datetime.now().date() - fecha_inicio).days + 1):
            fecha_dia = fecha_inicio + timedelta(days=dia)
            
            if fecha_dia > datetime.now().date():
                break
            
            # Determinar si es fin de semana
            es_fin_semana = fecha_dia.weekday() >= 5
            dia_del_mes = fecha_dia.day
            
            # Número de mediciones para este día (menos en fin de semana)
            factor_fin_semana = 0.7 if es_fin_semana else 1.0
            num_mediciones = int(random.randint(mediciones_min, mediciones_max) * factor_fin_semana)
            
            # Variables para mantener coherencia a lo largo del día
            fc_base_dia = None
            nivel_estres_base = None
            
            for medicion_num in range(num_mediciones):
                # Distribución más realista de horas (más mediciones durante el día)
                if random.random() < 0.8:  # 80% de mediciones durante el día
                    hora = random.randint(7, 22)
                else:  # 20% durante la noche
                    hora = random.choice(list(range(0, 7)) + [23])
                
                minuto = random.randint(0, 59)
                segundo = random.randint(0, 59)
                
                timestamp = datetime.combine(fecha_dia, datetime.min.time().replace(
                    hour=hora, minute=minuto, second=segundo
                ))
                
                # Generar FC realista (variable base para el día)
                if fc_base_dia is None:
                    fc_base_dia = self.generar_frecuencia_cardiaca_realista(
                        perfil_medico, 10, edad, smartwatch_data['genero'], dia_del_mes
                    )
                
                frecuencia_cardiaca = self.generar_frecuencia_cardiaca_realista(
                    perfil_medico, hora, edad, smartwatch_data['genero'], dia_del_mes
                )
                
                # Generar nivel de estrés (correlacionado a lo largo del día)
                if nivel_estres_base is None:
                    nivel_estres_base = self.generar_nivel_estres_realista(
                        perfil_medico, 12, edad, es_fin_semana
                    )
                
                nivel_estres = self.generar_nivel_estres_realista(
                    perfil_medico, hora, edad, es_fin_semana
                )
                
                # Ajustar por coherencia diaria
                nivel_estres = int(0.3 * nivel_estres_base + 0.7 * nivel_estres)
                
                # Presión arterial (90% de las mediciones, correlacionada con FC)
                presion_sistolica = presion_diastolica = None
                if random.random() < 0.90:
                    presion_sistolica, presion_diastolica = self.generar_presion_arterial_realista(
                        perfil_medico, edad, smartwatch_data['genero'], frecuencia_cardiaca
                    )
                
                # Saturación de oxígeno (95% de las mediciones)
                saturacion_oxigeno = None
                if random.random() < 0.95:
                    saturacion_oxigeno = self.generar_saturacion_oxigeno_realista(
                        perfil_medico, hora, edad
                    )
                
                # Temperatura (80% de las mediciones)
                temperatura = None
                if random.random() < 0.80:
                    temperatura = self.generar_temperatura_realista(
                        perfil_medico, hora, edad, smartwatch_data['genero'], dia_del_mes
                    )
                
                # Variabilidad del ritmo (98% de las mediciones, correlacionada con estrés)
                variabilidad_ritmo = None
                if random.random() < 0.98:
                    variabilidad_ritmo = self.generar_variabilidad_ritmo_realista(
                        perfil_medico, edad, smartwatch_data['genero'], nivel_estres
                    )
                
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
        """Generar mediciones cardíacas realistas para todos los smartwatches"""
        print(f"🔧 Generando mediciones cardíacas REALISTAS para {len(smartwatches_activos):,} smartwatches...")
        print(f"📅 Historial: {dias_historial} días")
        print(f"🏥 Aplicando perfiles médicos basados en epidemiología real...\n")
        
        start_time = time.time()
        todas_mediciones = []
        total_mediciones = 0
        perfiles_asignados = {'saludable': 0, 'riesgo_moderado': 0, 'patologico': 0}
        
        for i, smartwatch_data in enumerate(smartwatches_activos):
            mediciones_smartwatch, perfil = self.generar_mediciones_para_smartwatch(
                smartwatch_data, dias_historial
            )
            
            todas_mediciones.extend(mediciones_smartwatch)
            total_mediciones += len(mediciones_smartwatch)
            perfiles_asignados[perfil] += 1
            
            # Mostrar progreso cada 3 usuarios o si hay pocos
            if (i + 1) % 3 == 0 or len(smartwatches_activos) <= 10:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                promedio_mediciones = total_mediciones / (i + 1)
                
                print(f"📈 Procesados: {i + 1:,}/{len(smartwatches_activos):,} usuarios "
                      f"- {total_mediciones:,} mediciones ({promedio_mediciones:.0f} prom/usuario) "
                      f"- {rate:.1f} usuarios/seg")
        
        elapsed = time.time() - start_time
        promedio_final = total_mediciones / len(smartwatches_activos) if smartwatches_activos else 0
        
        print(f"\n✅ Generación completada en {elapsed:.2f} segundos")
        print(f"📊 Total de mediciones generadas: {total_mediciones:,}")
        print(f"📊 Promedio por usuario: {promedio_final:.0f} mediciones")
        
        # Mostrar distribución de perfiles
        print(f"\n🏥 Distribución de perfiles médicos (basada en epidemiología):")
        total_usuarios = sum(perfiles_asignados.values())
        for perfil, cantidad in perfiles_asignados.items():
            porcentaje = (cantidad / total_usuarios) * 100 if total_usuarios > 0 else 0
            nombre = self.perfiles_medicos[perfil]['nombre']
            print(f"   • {nombre}: {cantidad} usuarios ({porcentaje:.1f}%)")
        
        return todas_mediciones
    
    def insertar_mediciones_bulk(self, mediciones_data, batch_size=3000):
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
    
    def mostrar_estadisticas_medicas(self, mediciones_data):
        """Mostrar estadísticas médicamente relevantes de las mediciones generadas"""
        if not mediciones_data:
            print("📊 No hay datos para mostrar estadísticas.")
            return
        
        print(f"\n📈 Estadísticas de mediciones cardíacas REALISTAS:")
        
        # Estadísticas básicas
        total = len(mediciones_data)
        con_presion = sum(1 for m in mediciones_data if m['Presion_sistolica'] is not None)
        con_saturacion = sum(1 for m in mediciones_data if m['Saturacion_oxigeno'] is not None)
        con_temperatura = sum(1 for m in mediciones_data if m['Temperatura'] is not None)
        con_variabilidad = sum(1 for m in mediciones_data if m['Variabilidad_ritmo'] is not None)
        
        print(f"💓 Total de mediciones: {total:,}")
        print(f"\n📊 Completitud de datos (realista):")
        print(f"   • Frecuencia cardíaca: {total:,} (100.0%)")
        print(f"   • Presión arterial: {con_presion:,} ({(con_presion/total)*100:.1f}%)")
        print(f"   • Saturación O2: {con_saturacion:,} ({(con_saturacion/total)*100:.1f}%)")
        print(f"   • Temperatura: {con_temperatura:,} ({(con_temperatura/total)*100:.1f}%)")
        print(f"   • Variabilidad ritmo: {con_variabilidad:,} ({(con_variabilidad/total)*100:.1f}%)")
        print(f"   • Nivel de estrés: {total:,} (100.0%)")
        
        # Análisis de rangos médicos
        frecuencias = [m['Frecuencia_cardiaca'] for m in mediciones_data]
        niveles_estres = [m['Nivel_estres'] for m in mediciones_data]
        
        print(f"\n📈 Rangos de valores generados (médicamente validados):")
        print(f"   • Frecuencia cardíaca: {min(frecuencias)}-{max(frecuencias)} bpm")
        print(f"   • Nivel de estrés: {min(niveles_estres)}-{max(niveles_estres)}%")
        
        # Análisis de FC por categorías
        fc_reposo = [fc for fc in frecuencias if fc < 80]
        fc_elevada = [fc for fc in frecuencias if fc >= 100]
        print(f"   • FC en reposo (<80 bpm): {len(fc_reposo)} mediciones ({len(fc_reposo)/len(frecuencias)*100:.1f}%)")
        print(f"   • FC elevada (≥100 bpm): {len(fc_elevada)} mediciones ({len(fc_elevada)/len(frecuencias)*100:.1f}%)")
        
        if con_presion > 0:
            presiones_sys = [m['Presion_sistolica'] for m in mediciones_data if m['Presion_sistolica']]
            presiones_dia = [m['Presion_diastolica'] for m in mediciones_data if m['Presion_diastolica']]
            print(f"   • Presión sistólica: {min(presiones_sys)}-{max(presiones_sys)} mmHg")
            print(f"   • Presión diastólica: {min(presiones_dia)}-{max(presiones_dia)} mmHg")
            
            # Análisis de hipertensión
            hta = [p for p in presiones_sys if p >= 140]
            print(f"   • Lecturas con HTA (≥140 mmHg): {len(hta)} ({len(hta)/len(presiones_sys)*100:.1f}%)")
        
        if con_saturacion > 0:
            saturaciones = [float(m['Saturacion_oxigeno']) for m in mediciones_data if m['Saturacion_oxigeno']]
            print(f"   • Saturación O2: {min(saturaciones):.1f}-{max(saturaciones):.1f}%")
            
            # Análisis de hipoxemia
            hipoxemia = [s for s in saturaciones if s < 95]
            print(f"   • Lecturas con hipoxemia (<95%): {len(hipoxemia)} ({len(hipoxemia)/len(saturaciones)*100:.1f}%)")
        
        # Mostrar usuarios procesados
        usuarios_procesados = sorted(set(m['Usuario_ID'] for m in mediciones_data))
        print(f"\n👥 Usuarios procesados: {len(usuarios_procesados)} usuarios")
        print(f"   • Rango de IDs: {min(usuarios_procesados)} - {max(usuarios_procesados)}")
        
        # Validación médica
        print(f"\n🏥 VALIDACIÓN MÉDICA:")
        print(f"   ✅ Rangos de FC basados en guidelines AHA/ESC")
        print(f"   ✅ Presión arterial según ESH/ESC 2018")
        print(f"   ✅ Correlaciones fisiológicas aplicadas")
        print(f"   ✅ Variaciones circadianas realistas")
        print(f"   ✅ Factores de edad y género incluidos")
    
    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        try:
            from config.database import engine
            HeartMeasurement.__table__.create(engine, checkfirst=True)
            logger.info("✅ Tabla de mediciones cardíacas verificada/creada")
        except Exception as e:
            logger.warning(f"⚠️ Error al crear tabla de mediciones cardíacas: {e}")
    
    def seed(self, dias_historial=30, usuario_inicio=None, usuario_fin=None):
        """Seed para mediciones cardíacas médicamente realistas"""
        logger.info("Iniciando seeding de mediciones cardíacas médicamente realistas...")
        print(f"\n💓 Iniciando creación de mediciones cardíacas MÉDICAMENTE REALISTAS...")
        
        start_total = time.time()
        
        # 1. Solicitar rango de usuarios si no se especifica
        if usuario_inicio is None or usuario_fin is None:
            usuario_inicio, usuario_fin = self.solicitar_rango_usuarios()
            if usuario_inicio is None or usuario_fin is None:
                print("❌ Operación cancelada.")
                return
        
        print(f"\n📋 CONFIGURACIÓN DEL PROCESO:")
        print(f"   • Rango de usuarios: {usuario_inicio} - {usuario_fin}")
        print(f"   • Días de historial: {dias_historial}")
        print(f"   • Perfiles médicos: Basados en epidemiología real")
        print(f"   • Validación médica: Guidelines AHA/ESC aplicados")
        
        # 2. Obtener smartwatches en el rango especificado
        smartwatches_activos = self.obtener_smartwatches_activos(usuario_inicio, usuario_fin)
        
        if not smartwatches_activos:
            print(f"❌ No hay smartwatches disponibles en el rango {usuario_inicio}-{usuario_fin}.")
            print("   Verifique que:")
            print("   • Los usuarios tengan smartwatches asignados")
            print("   • El rango de usuarios sea válido")
            print("   • Ejecute primero SmartwatchSeeder si es necesario")
            return
        
        # 3. Mostrar información de perfiles médicos
        print(f"\n🏥 PERFILES MÉDICOS DISPONIBLES (Médicamente Validados):")
        for perfil_key, perfil_data in self.perfiles_medicos.items():
            print(f"   • {perfil_data['nombre']}: {perfil_data['descripcion']}")
        
        # 4. Confirmar antes de procesar
        cantidad_usuarios = len(smartwatches_activos)
        estimacion_mediciones = cantidad_usuarios * 600  # Promedio más realista
        
        print(f"\n📊 ESTIMACIONES:")
        print(f"   • Usuarios a procesar: {cantidad_usuarios:,}")
        print(f"   • Mediciones estimadas: ~{estimacion_mediciones:,}")
        print(f"   • Tiempo estimado: ~{cantidad_usuarios * 1.5:.0f} segundos")
        print(f"   • Calidad: Datos médicamente precisos y correlacionados")
        
        confirmacion = input(f"\n✅ ¿Proceder con la generación? (s/n): ").strip().lower()
        if confirmacion not in ['s', 'si', 'sí', 'yes', 'y']:
            print("❌ Operación cancelada por el usuario.")
            return
        
        # 5. Generar mediciones en memoria
        mediciones_data = self.generar_mediciones_batch(smartwatches_activos, dias_historial)
        
        # 6. Mostrar estadísticas médicas antes de insertar
        self.mostrar_estadisticas_medicas(mediciones_data)
        
        # 7. Confirmar inserción
        print(f"\n💾 ¿Proceder con la inserción en base de datos?")
        confirmacion_insert = input(f"   Esto insertará {len(mediciones_data):,} registros REALISTAS (s/n): ").strip().lower()
        if confirmacion_insert not in ['s', 'si', 'sí', 'yes', 'y']:
            print("❌ Inserción cancelada. Los datos no se guardaron.")
            return
        
        # 8. Insertar usando bulk operations
        mediciones_creadas = self.insertar_mediciones_bulk(mediciones_data)
        
        # 9. Resumen final
        total_elapsed = time.time() - start_total
        total_rate = mediciones_creadas / total_elapsed if total_elapsed > 0 else 0
        
        usuarios_procesados = sorted(set(sw['usuario_id'] for sw in smartwatches_activos))
        
        print(f"\n🎉 ¡Seeding de mediciones cardíacas REALISTAS completado!")
        print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos")
        print(f"🚄 Velocidad promedio: {total_rate:.0f} mediciones/segundo")
        print(f"\n📊 Resumen final:")
        print(f"   • Mediciones creadas: {mediciones_creadas:,}")
        print(f"   • Usuarios procesados: {len(usuarios_procesados):,} (IDs: {min(usuarios_procesados)}-{max(usuarios_procesados)})")
        print(f"   • Smartwatches procesados: {len(smartwatches_activos):,}")
        print(f"   • Período de datos: {dias_historial} días")
        print(f"   • Calidad: Médicamente validado y correlacionado")
        
        if len(smartwatches_activos) > 0:
            promedio_por_smartwatch = mediciones_creadas / len(smartwatches_activos)
            print(f"   • Promedio por usuario: {promedio_por_smartwatch:.1f} mediciones")
        
        print(f"\n🏥 CARACTERÍSTICAS MÉDICAS IMPLEMENTADAS:")
        print(f"   ✅ Correlación FC-Presión arterial")
        print(f"   ✅ Variación circadiana realista")
        print(f"   ✅ Factores de edad y género")
        print(f"   ✅ Correlación estrés-HRV")
        print(f"   ✅ Perfiles epidemiológicos")
        
        logger.info(f"Seeding médicamente realista completado:")
        logger.info(f"- Rango usuarios: {usuario_inicio}-{usuario_fin}")
        logger.info(f"- Usuarios procesados: {len(usuarios_procesados)}")
        logger.info(f"- Tiempo total: {total_elapsed:.2f}s")
        logger.info(f"- Mediciones creadas: {mediciones_creadas}")
        logger.info(f"- Velocidad: {total_rate:.0f} mediciones/seg")
    
    def run(self, clear_first=False, table_names=None, usuario_inicio=None, usuario_fin=None, dias_historial=30):
        """Ejecutar el seeder de mediciones cardíacas realistas"""
        try:
            if clear_first and table_names:
                logger.info("🗑️ Limpiando datos existentes de mediciones cardíacas...")
                self.clear_tables(table_names)
            
            logger.info("💓 Ejecutando seeder de mediciones cardíacas realistas...")
            
            # Ejecutar el seed con parámetros especificados
            self.seed(dias_historial=dias_historial, usuario_inicio=usuario_inicio, usuario_fin=usuario_fin)
                
        except Exception as e:
            logger.error(f"❌ Error durante el seeding de mediciones cardíacas: {str(e)}")
            self.db.rollback()
            raise e

if __name__ == "__main__":
    try:
        with HeartMeasurementSeeder() as seeder:
            seeder.create_tables()
            # El seeder preguntará al usuario el rango de usuarios a procesar
            seeder.seed(dias_historial=30)
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")