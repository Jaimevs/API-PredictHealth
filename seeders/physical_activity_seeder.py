from .base_seeder import BaseSeeder
from models.physical_activity import PhysicalActivity
from datetime import datetime, timedelta
import random
import logging
import time
from sqlalchemy import text

logger = logging.getLogger(__name__)

class PhysicalActivitySeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Perfiles de actividad física realistas y simplificados
        self.activity_profiles = {
            'sedentario': {
                'nombre': 'Persona Sedentaria',
                'probabilidad': 0.30,
                'pasos': (1500, 4000),
                'distancia': (1.0, 3.0),
                'calorias': (1400, 1900),
                'minutos_actividad': (10, 35),
                'pisos': (0, 4)
            },
            'moderado': {
                'nombre': 'Actividad Moderada',
                'probabilidad': 0.45,
                'pasos': (4000, 8500),
                'distancia': (3.0, 6.5),
                'calorias': (1900, 2600),
                'minutos_actividad': (35, 80),
                'pisos': (4, 10)
            },
            'activo': {
                'nombre': 'Persona Activa',
                'probabilidad': 0.20,
                'pasos': (8500, 14000),
                'distancia': (6.5, 11.0),
                'calorias': (2600, 3400),
                'minutos_actividad': (80, 130),
                'pisos': (10, 18)
            },
            'muy_activo': {
                'nombre': 'Muy Activo/Deportista',
                'probabilidad': 0.05,
                'pasos': (14000, 25000),
                'distancia': (11.0, 20.0),
                'calorias': (3400, 4500),
                'minutos_actividad': (130, 200),
                'pisos': (18, 30)
            }
        }
    
    def obtener_total_usuarios_con_smartwatch(self):
        """Obtener el total de usuarios con smartwatch disponibles"""
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
    
    def obtener_usuarios_con_smartwatch_optimizado(self, usuario_inicio=None, usuario_fin=None):
        """Obtener usuarios con smartwatch de forma optimizada"""
        print("🔍 Obteniendo usuarios con smartwatch...")
        start_time = time.time()
        
        # Query optimizada para obtener usuario y smartwatch en una sola consulta
        query_base = """
            SELECT DISTINCT
                s.Usuario_ID,
                s.ID as smartwatch_id,
                p.Fecha_Nacimiento,
                p.Genero
            FROM tbb_smartwatches s
            INNER JOIN tbb_usuarios u ON s.Usuario_ID = u.ID
            INNER JOIN tbb_personas p ON u.Persona_Id = p.ID
            WHERE s.Estatus = 1 
            AND u.Estatus = 1 
            AND p.Estatus = 1
        """
        
        # Agregar filtro de rango si se especifica
        if usuario_inicio is not None and usuario_fin is not None:
            query_base += f" AND s.Usuario_ID BETWEEN {usuario_inicio} AND {usuario_fin}"
            print(f"📌 Filtrando usuarios del ID {usuario_inicio} al {usuario_fin}")
        
        query_base += " ORDER BY s.Usuario_ID LIMIT 1000"  # Limitar para evitar sobrecarga
        
        query = text(query_base)
        result = self.db.execute(query).fetchall()
        
        usuarios_data = []
        for row in result:
            usuario_data = {
                'usuario_id': row[0],
                'smartwatch_id': row[1],
                'fecha_nacimiento': row[2],
                'genero': row[3]
            }
            usuarios_data.append(usuario_data)
        
        elapsed = time.time() - start_time
        print(f"✅ Consulta completada en {elapsed:.2f} segundos")
        print(f"📊 Usuarios encontrados: {len(usuarios_data):,}")
        
        return usuarios_data
    
    def calcular_edad(self, fecha_nacimiento):
        """Calcular edad actual"""
        if not fecha_nacimiento:
            return 30  # Edad default
        
        today = datetime.now().date()
        if isinstance(fecha_nacimiento, datetime):
            fecha_nacimiento = fecha_nacimiento.date()
        
        return today.year - fecha_nacimiento.year - (
            (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
    
    def asignar_perfil_actividad(self, edad, genero):
        """Asignar perfil de actividad basado en edad y género"""
        # Probabilidades base
        prob_sedentario = 0.30
        prob_moderado = 0.45
        prob_activo = 0.20
        prob_muy_activo = 0.05
        
        # Ajustes por edad
        if edad < 25:
            # Jóvenes más activos
            prob_sedentario = 0.20
            prob_moderado = 0.40
            prob_activo = 0.30
            prob_muy_activo = 0.10
        elif edad > 60:
            # Adultos mayores más sedentarios
            prob_sedentario = 0.50
            prob_moderado = 0.40
            prob_activo = 0.10
            prob_muy_activo = 0.00
        
        # Seleccionar perfil
        rand = random.random()
        if rand < prob_sedentario:
            return 'sedentario'
        elif rand < prob_sedentario + prob_moderado:
            return 'moderado'
        elif rand < prob_sedentario + prob_moderado + prob_activo:
            return 'activo'
        else:
            return 'muy_activo'
    
    def generar_actividad_realista(self, perfil_nombre, edad, genero, usuario_id, smartwatch_id):
        """Generar una actividad física realista para un usuario"""
        perfil = self.activity_profiles[perfil_nombre]
        
        # Factores de ajuste por edad
        if edad < 25:
            factor_edad = 1.15  # Más activos
        elif edad > 60:
            factor_edad = 0.75  # Menos activos
        elif edad > 45:
            factor_edad = 0.90  # Ligeramente menos activos
        else:
            factor_edad = 1.0
        
        # Factores de ajuste por género (estadísticamente hombres caminan más)
        if genero and str(genero).upper() in ['M', 'MASCULINO', '1']:
            factor_genero = 1.05
        else:
            factor_genero = 0.95
        
        # Generar valores con factores de ajuste
        factor_total = factor_edad * factor_genero
        
        # Generar valores base
        pasos_base = random.randint(*perfil['pasos'])
        distancia_base = random.uniform(*perfil['distancia'])
        calorias_base = random.randint(*perfil['calorias'])
        minutos_base = random.randint(*perfil['minutos_actividad'])
        pisos_base = random.randint(*perfil['pisos'])
        
        # Aplicar factores y variación natural
        variacion = random.uniform(0.85, 1.15)  # ±15% de variación
        
        pasos = max(500, int(pasos_base * factor_total * variacion))
        distancia = max(0.5, round(distancia_base * factor_total * variacion, 2))
        calorias = max(800, int(calorias_base * factor_total * variacion))
        minutos = max(5, int(minutos_base * factor_total * variacion))
        pisos = max(0, int(pisos_base * factor_total * variacion))
        
        # Correlación realista: distancia aproximada basada en pasos
        # Promedio: 1 km ≈ 1300 pasos
        distancia_calculada = pasos / 1300
        distancia = round((distancia + distancia_calculada) / 2, 2)
        
        # Timestamp reciente (últimos 7 días)
        dias_atras = random.randint(0, 7)
        fecha_registro = datetime.now() - timedelta(days=dias_atras)
        fecha_registro = fecha_registro.replace(
            hour=random.randint(6, 22),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        return {
            'Usuario_ID': usuario_id,
            'Smartwatch_ID': smartwatch_id,
            'Pasos': pasos,
            'Distancia_km': distancia,
            'Calorias_quemadas': calorias,
            'Minutos_actividad': minutos,
            'Pisos_subidos': pisos,
            'Estatus': True,
            'Fecha_Registro': fecha_registro
        }
    
    def generar_actividades_batch(self, usuarios_data):
        """Generar actividades para todos los usuarios de forma optimizada"""
        print(f"🏃 Generando actividad física para {len(usuarios_data):,} usuarios...")
        print(f"📊 Distribuyendo perfiles de actividad realistas...\n")
        
        start_time = time.time()
        actividades = []
        perfiles_asignados = {'sedentario': 0, 'moderado': 0, 'activo': 0, 'muy_activo': 0}
        
        for i, usuario_data in enumerate(usuarios_data):
            # Calcular edad
            edad = self.calcular_edad(usuario_data['fecha_nacimiento'])
            
            # Asignar perfil de actividad
            perfil = self.asignar_perfil_actividad(edad, usuario_data['genero'])
            perfiles_asignados[perfil] += 1
            
            # Generar actividad
            actividad = self.generar_actividad_realista(
                perfil, edad, usuario_data['genero'],
                usuario_data['usuario_id'], usuario_data['smartwatch_id']
            )
            
            actividades.append(actividad)
            
            # Mostrar progreso cada 100 usuarios o si hay pocos
            if (i + 1) % 100 == 0 or len(usuarios_data) <= 50:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                
                print(f"📈 Procesados: {i + 1:,}/{len(usuarios_data):,} usuarios "
                      f"- {rate:.1f} usuarios/seg")
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ Generación completada en {elapsed:.2f} segundos")
        print(f"📊 Total de actividades generadas: {len(actividades):,}")
        
        # Mostrar distribución de perfiles
        print(f"\n🏃 Distribución de perfiles de actividad:")
        total_usuarios = sum(perfiles_asignados.values())
        for perfil, cantidad in perfiles_asignados.items():
            porcentaje = (cantidad / total_usuarios) * 100 if total_usuarios > 0 else 0
            nombre = self.activity_profiles[perfil]['nombre']
            print(f"   • {nombre}: {cantidad} usuarios ({porcentaje:.1f}%)")
        
        return actividades
    
    def insertar_actividades_bulk(self, actividades_data, batch_size=2000):
        """Insertar actividades usando bulk insert optimizado"""
        total_actividades = len(actividades_data)
        if total_actividades == 0:
            print("🏃 No hay actividades para insertar.")
            return 0
        
        print(f"💾 Insertando {total_actividades:,} actividades en lotes de {batch_size:,}...")
        
        start_time = time.time()
        actividades_insertadas = 0
        
        for i in range(0, total_actividades, batch_size):
            batch = actividades_data[i:i + batch_size]
            
            try:
                self.db.bulk_insert_mappings(PhysicalActivity, batch)
                self.db.commit()
                
                actividades_insertadas += len(batch)
                
                # Mostrar progreso
                elapsed = time.time() - start_time
                if elapsed > 0:
                    rate = actividades_insertadas / elapsed
                    porcentaje = (actividades_insertadas / total_actividades) * 100
                    
                    print(f"📈 Insertadas: {actividades_insertadas:,}/{total_actividades:,} "
                          f"({porcentaje:.1f}%) - {rate:.0f} actividades/seg")
                
            except Exception as e:
                logger.error(f"Error insertando lote {i//batch_size + 1}: {e}")
                self.db.rollback()
                raise
        
        elapsed = time.time() - start_time
        final_rate = actividades_insertadas / elapsed if elapsed > 0 else 0
        
        print(f"✅ Inserción completada en {elapsed:.2f} segundos ({final_rate:.0f} actividades/seg)")
        
        return actividades_insertadas
    
    def mostrar_estadisticas(self, actividades_data):
        """Mostrar estadísticas de las actividades generadas"""
        if not actividades_data:
            print("📊 No hay datos para mostrar estadísticas.")
            return
        
        print(f"\n📈 Estadísticas de actividades físicas generadas:")
        
        # Estadísticas básicas
        total = len(actividades_data)
        pasos_total = sum(a['Pasos'] for a in actividades_data)
        distancia_total = sum(a['Distancia_km'] for a in actividades_data)
        calorias_total = sum(a['Calorias_quemadas'] for a in actividades_data)
        
        print(f"🏃 Total de actividades: {total:,}")
        print(f"👣 Pasos promedio: {pasos_total // total:,}")
        print(f"🛣️  Distancia promedio: {distancia_total / total:.2f} km")
        print(f"🔥 Calorías promedio: {calorias_total // total:,}")
        
        # Rangos
        pasos = [a['Pasos'] for a in actividades_data]
        distancias = [a['Distancia_km'] for a in actividades_data]
        calorias = [a['Calorias_quemadas'] for a in actividades_data]
        minutos = [a['Minutos_actividad'] for a in actividades_data]
        
        print(f"\n📊 Rangos de valores:")
        print(f"   • Pasos: {min(pasos):,} - {max(pasos):,}")
        print(f"   • Distancia: {min(distancias):.1f} - {max(distancias):.1f} km")
        print(f"   • Calorías: {min(calorias):,} - {max(calorias):,}")
        print(f"   • Minutos activos: {min(minutos)} - {max(minutos)}")
        
        # Mostrar usuarios procesados
        usuarios_procesados = sorted(set(a['Usuario_ID'] for a in actividades_data))
        print(f"\n👥 Usuarios con actividad: {len(usuarios_procesados)} usuarios")
        if usuarios_procesados:
            print(f"   • Rango de IDs: {min(usuarios_procesados)} - {max(usuarios_procesados)}")
    
    def solicitar_rango_usuarios(self):
        """Solicitar rango de usuarios (reutilizar del heart seeder)"""
        total_usuarios = self.obtener_total_usuarios_con_smartwatch()
        
        if total_usuarios == 0:
            print("❌ No hay usuarios con smartwatches disponibles.")
            return None, None
        
        print(f"\n📊 INFORMACIÓN DE USUARIOS DISPONIBLES:")
        print(f"   • Total de usuarios con smartwatches: {total_usuarios:,}")
        print(f"   • Registro: Una actividad por usuario")
        print(f"   • Estimación: Procesamiento muy rápido")
        
        while True:
            print(f"\n🎯 OPCIONES DE PROCESAMIENTO:")
            print(f"   1. Primeros 100 usuarios (recomendado)")
            print(f"   2. Primeros 1000 usuarios")
            print(f"   3. Todos los usuarios")
            print(f"   4. Cancelar")
            
            try:
                opcion = input("\n📝 Seleccione una opción (1-4): ").strip()
                
                if opcion == "1":
                    return 1, 100
                elif opcion == "2":
                    return 1, 1000
                elif opcion == "3":
                    confirmacion = input(f"⚠️  ¿Procesar TODOS los {total_usuarios:,} usuarios? (s/n): ")
                    if confirmacion.lower() in ['s', 'si', 'sí', 'yes', 'y']:
                        return None, None  # Sin límite
                    else:
                        continue
                elif opcion == "4":
                    print("❌ Operación cancelada.")
                    return None, None
                else:
                    print("❌ Opción inválida. Por favor seleccione 1-4.")
                    
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada por el usuario.")
                return None, None
    
    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        try:
            from config.database import engine
            PhysicalActivity.__table__.create(engine, checkfirst=True)
            logger.info("✅ Tabla de actividad física verificada/creada")
        except Exception as e:
            logger.warning(f"⚠️ Error al crear tabla de actividad física: {e}")
    
    def seed(self, usuario_inicio=None, usuario_fin=None):
        """Seed optimizado para actividad física"""
        logger.info("Iniciando seeding optimizado de actividad física...")
        print(f"\n🏃 Iniciando creación de actividades físicas (1 por usuario)...")
        
        start_total = time.time()
        
        # 1. Solicitar rango si no se especifica
        if usuario_inicio is None and usuario_fin is None:
            usuario_inicio, usuario_fin = self.solicitar_rango_usuarios()
            if usuario_inicio is None and usuario_fin is None:
                print("❌ Operación cancelada.")
                return
        
        # 2. Obtener usuarios con smartwatch
        usuarios_data = self.obtener_usuarios_con_smartwatch_optimizado(usuario_inicio, usuario_fin)
        
        if not usuarios_data:
            print("❌ No hay usuarios con smartwatch disponibles.")
            return
        
        print(f"\n📋 CONFIGURACIÓN:")
        print(f"   • Usuarios a procesar: {len(usuarios_data):,}")
        print(f"   • Actividades por usuario: 1")
        print(f"   • Perfiles: 4 tipos (sedentario, moderado, activo, muy activo)")
        
        # 3. Confirmar procesamiento
        confirmacion = input(f"\n✅ ¿Proceder con la generación? (s/n): ").strip().lower()
        if confirmacion not in ['s', 'si', 'sí', 'yes', 'y']:
            print("❌ Operación cancelada.")
            return
        
        # 4. Generar actividades
        actividades_data = self.generar_actividades_batch(usuarios_data)
        
        # 5. Mostrar estadísticas
        self.mostrar_estadisticas(actividades_data)
        
        # 6. Confirmar inserción
        print(f"\n💾 ¿Proceder con la inserción?")
        confirmacion_insert = input(f"   Esto insertará {len(actividades_data):,} actividades (s/n): ").strip().lower()
        if confirmacion_insert not in ['s', 'si', 'sí', 'yes', 'y']:
            print("❌ Inserción cancelada.")
            return
        
        # 7. Insertar
        actividades_creadas = self.insertar_actividades_bulk(actividades_data)
        
        # 8. Resumen final
        total_elapsed = time.time() - start_total
        
        print(f"\n🎉 ¡Seeding de actividad física completado!")
        print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos")
        print(f"📊 Resumen final:")
        print(f"   • Actividades creadas: {actividades_creadas:,}")
        print(f"   • Usuarios procesados: {len(usuarios_data):,}")
        print(f"   • Velocidad: {actividades_creadas/total_elapsed:.0f} actividades/seg")
        
        logger.info(f"Seeding de actividad física completado: {actividades_creadas} registros en {total_elapsed:.2f}s")
    
    def run(self, clear_first=False, table_names=None, usuario_inicio=None, usuario_fin=None):
        """Ejecutar el seeder optimizado"""
        try:
            if clear_first and table_names:
                logger.info("🗑️ Limpiando datos existentes...")
                self.clear_tables(table_names)
            
            logger.info("🏃 Ejecutando seeder de actividad física optimizado...")
            self.seed(usuario_inicio, usuario_fin)
                
        except Exception as e:
            logger.error(f"❌ Error durante el seeding: {str(e)}")
            self.db.rollback()
            raise e

if __name__ == "__main__":
    try:
        with PhysicalActivitySeeder() as seeder:
            seeder.create_tables()
            seeder.seed()
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")