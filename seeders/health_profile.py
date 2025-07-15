from .base_seeder import BaseSeeder
from models.health_profile import HealthProfile, BloodTypeEnum
from models.user import User
from models.person import Person, GenderEnum
import logging
import random
import time
from datetime import date, datetime
from sqlalchemy import text

logger = logging.getLogger(__name__)

class HealthProfileSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Distribución realista de tipos de sangre (basada en población mexicana)
        # IMPORTANTE: Usar los nombres NUEVOS del enum
        self.tipos_sangre_distribucion = [
            (BloodTypeEnum.O_PLUS, 0.60),     # 60% - O+
            (BloodTypeEnum.A_PLUS, 0.27),     # 27% - A+
            (BloodTypeEnum.B_PLUS, 0.08),     # 8% - B+
            (BloodTypeEnum.O_MINUS, 0.03),    # 3% - O-
            (BloodTypeEnum.A_MINUS, 0.015),   # 1.5% - A-
            (BloodTypeEnum.AB_PLUS, 0.003),   # 0.3% - AB+
            (BloodTypeEnum.B_MINUS, 0.002),   # 0.2% - B-
            (BloodTypeEnum.AB_MINUS, 0.0005), # 0.05% - AB-
        ]
        
        # Estadísticas de salud realistas (basadas en datos de México)
        self.estadisticas_salud = {
            'fumador': 0.17,        # 17% fumadores
            'diabetico': 0.105,     # 10.5% diabéticos
            'hipertenso': 0.25,     # 25% hipertensos
            'historial_cardiaco': 0.08  # 8% con historial cardíaco
        }
        
        # Rangos de peso y altura por género y edad
        self.rangos_fisicos = {
            'hombre': {
                'peso_base': (70, 85),      # kg
                'altura_base': (165, 180),  # cm
                'variacion_edad': 0.8       # factor de variación por edad
            },
            'mujer': {
                'peso_base': (55, 70),      # kg
                'altura_base': (155, 170),  # cm
                'variacion_edad': 0.7       # factor de variación por edad
            }
        }
    
    def calcular_edad(self, fecha_nacimiento):
        """Calcular edad actual basada en fecha de nacimiento"""
        today = date.today()
        return today.year - fecha_nacimiento.year - (
            (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
    
    def generar_tipo_sangre(self):
        """Generar tipo de sangre con distribución realista"""
        rand = random.random()
        acumulado = 0
        
        for tipo_sangre, probabilidad in self.tipos_sangre_distribucion:
            acumulado += probabilidad
            if rand <= acumulado:
                return tipo_sangre
        
        # Fallback (no debería llegar aquí)
        return BloodTypeEnum.O_PLUS
    
    def generar_peso_altura(self, genero, edad):
        """Generar peso y altura realistas basados en género y edad"""
        es_hombre = genero == GenderEnum.H
        config = self.rangos_fisicos['hombre' if es_hombre else 'mujer']
        
        # Base según género
        peso_min, peso_max = config['peso_base']
        altura_min, altura_max = config['altura_base']
        
        # Ajuste por edad
        factor_edad = 1.0
        if edad < 25:
            factor_edad = 0.95  # Más delgados cuando jóvenes
        elif edad > 50:
            factor_edad = 1.1   # Tendencia a ganar peso con la edad
        elif edad > 65:
            factor_edad = 0.9   # Pérdida de peso en edad avanzada
        
        # Generar altura (más estable, menos afectada por edad)
        altura = round(random.uniform(altura_min, altura_max), 1)
        
        # Generar peso (más variable, afectado por edad)
        peso_base = random.uniform(peso_min, peso_max)
        peso = round(peso_base * factor_edad, 1)
        
        # Asegurar rangos mínimos razonables
        peso = max(peso, 40.0)
        altura = max(altura, 140.0)
        
        return peso, altura
    
    def generar_condiciones_salud(self, edad, genero):
        """Generar condiciones de salud basadas en estadísticas reales"""
        # Factores de riesgo por edad
        factor_edad = 1.0
        if edad < 30:
            factor_edad = 0.3  # Menos problemas en jóvenes
        elif edad < 50:
            factor_edad = 0.7  # Riesgo moderado
        elif edad < 65:
            factor_edad = 1.2  # Riesgo aumentado
        else:
            factor_edad = 1.8  # Riesgo alto en adultos mayores
        
        # Factores de riesgo por género (algunos problemas son más comunes en cierto género)
        factor_genero = {
            'fumador': 1.2 if genero == GenderEnum.H else 0.8,
            'diabetico': 1.1 if genero == GenderEnum.H else 0.9,
            'hipertenso': 1.1 if genero == GenderEnum.H else 0.9,
            'historial_cardiaco': 1.3 if genero == GenderEnum.H else 0.7
        }
        
        condiciones = {}
        
        for condicion, probabilidad_base in self.estadisticas_salud.items():
            probabilidad_ajustada = (
                probabilidad_base * 
                factor_edad * 
                factor_genero.get(condicion, 1.0)
            )
            
            # Limitar probabilidad máxima
            probabilidad_ajustada = min(probabilidad_ajustada, 0.7)
            
            condiciones[condicion] = random.random() < probabilidad_ajustada
        
        # Correlaciones entre condiciones (diabetes e hipertensión suelen ir juntas)
        if condiciones['diabetico'] and random.random() < 0.4:
            condiciones['hipertenso'] = True
        
        if condiciones['hipertenso'] and random.random() < 0.3:
            condiciones['historial_cardiaco'] = True
        
        if condiciones['fumador'] and random.random() < 0.2:
            condiciones['historial_cardiaco'] = True
        
        return condiciones
    
    def obtener_usuarios_sin_perfil(self):
        """Obtener usuarios que no tienen perfil de salud"""
        print("🔍 Verificando usuarios sin perfil de salud...")
        start_time = time.time()
        
        # Query optimizada para obtener usuarios sin perfil
        query = text("""
            SELECT u.ID, p.Genero, p.Fecha_Nacimiento
            FROM tbb_usuarios u
            INNER JOIN tbb_personas p ON u.Persona_Id = p.ID
            LEFT JOIN tbb_perfil_salud hp ON u.ID = hp.Usuario_ID
            WHERE u.Estatus = 1 
            AND p.Estatus = 1 
            AND hp.Usuario_ID IS NULL
        """)
        
        result = self.db.execute(query).fetchall()
        usuarios_sin_perfil = [
            {
                'usuario_id': row[0],
                'genero': GenderEnum(row[1]),
                'fecha_nacimiento': row[2]
            }
            for row in result
        ]
        
        elapsed = time.time() - start_time
        print(f"✅ Verificación completada en {elapsed:.2f} segundos")
        print(f"📊 Usuarios sin perfil encontrados: {len(usuarios_sin_perfil):,}")
        
        return usuarios_sin_perfil
    
    def generar_perfiles_batch(self, usuarios_sin_perfil):
        """Generar datos de perfiles de salud en lotes"""
        print(f"🔧 Generando perfiles de salud para {len(usuarios_sin_perfil):,} usuarios...")
        start_time = time.time()
        
        perfiles_data = []
        
        for i, usuario_data in enumerate(usuarios_sin_perfil):
            edad = self.calcular_edad(usuario_data['fecha_nacimiento'])
            genero = usuario_data['genero']
            
            # Generar datos físicos
            peso, altura = self.generar_peso_altura(genero, edad)
            
            # Generar tipo de sangre
            tipo_sangre = self.generar_tipo_sangre()
            
            # Generar condiciones de salud
            condiciones = self.generar_condiciones_salud(edad, genero)
            
            perfil_data = {
                'Usuario_ID': usuario_data['usuario_id'],
                'Peso_kg': peso,
                'Altura_cm': altura,
                'Tipo_sangre': tipo_sangre,
                'Fumador': condiciones['fumador'],
                'Diabetico': condiciones['diabetico'],
                'Hipertenso': condiciones['hipertenso'],
                'Historial_cardiaco': condiciones['historial_cardiaco'],
                'Estatus': True,
                'Fecha_Registro': datetime.now()
            }
            
            perfiles_data.append(perfil_data)
            
            # Mostrar progreso cada 1000 perfiles
            if (i + 1) % 1000 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"📈 Generados: {i + 1:,}/{len(usuarios_sin_perfil):,} ({rate:.0f} perfiles/seg)")
        
        elapsed = time.time() - start_time
        print(f"✅ Generación completada en {elapsed:.2f} segundos")
        
        return perfiles_data
    
    def insertar_perfiles_bulk(self, perfiles_data, batch_size=1000):
        """Insertar perfiles usando bulk insert"""
        total_perfiles = len(perfiles_data)
        print(f"💾 Insertando {total_perfiles:,} perfiles en lotes de {batch_size:,}...")
        
        start_time = time.time()
        perfiles_insertados = 0
        
        for i in range(0, total_perfiles, batch_size):
            batch = perfiles_data[i:i + batch_size]
            
            try:
                self.db.bulk_insert_mappings(HealthProfile, batch)
                self.db.commit()
                
                perfiles_insertados += len(batch)
                
                # Mostrar progreso
                elapsed = time.time() - start_time
                if elapsed > 0:
                    rate = perfiles_insertados / elapsed
                    porcentaje = (perfiles_insertados / total_perfiles) * 100
                    
                    print(f"📈 Insertados: {perfiles_insertados:,}/{total_perfiles:,} "
                          f"({porcentaje:.1f}%) - {rate:.0f} perfiles/seg")
                
            except Exception as e:
                logger.error(f"Error insertando lote {i//batch_size + 1}: {e}")
                self.db.rollback()
                raise
        
        elapsed = time.time() - start_time
        final_rate = perfiles_insertados / elapsed if elapsed > 0 else 0
        
        print(f"✅ Inserción completada en {elapsed:.2f} segundos ({final_rate:.0f} perfiles/seg)")
        
        return perfiles_insertados
    
    def mostrar_estadisticas(self, perfiles_data):
        """Mostrar estadísticas de los perfiles generados"""
        if not perfiles_data:
            return
        
        print(f"\n📈 Estadísticas de perfiles generados:")
        
        # Tipos de sangre
        tipos_sangre = {}
        condiciones = {'Fumador': 0, 'Diabetico': 0, 'Hipertenso': 0, 'Historial_cardiaco': 0}
        
        for perfil in perfiles_data:
            # Contar tipos de sangre
            tipo = perfil['Tipo_sangre'].value
            tipos_sangre[tipo] = tipos_sangre.get(tipo, 0) + 1
            
            # Contar condiciones
            for condicion in condiciones:
                if perfil[condicion]:
                    condiciones[condicion] += 1
        
        total = len(perfiles_data)
        
        print(f"🩸 Distribución de tipos de sangre:")
        for tipo, cantidad in sorted(tipos_sangre.items()):
            porcentaje = (cantidad / total) * 100
            print(f"   • {tipo}: {cantidad:,} ({porcentaje:.1f}%)")
        
        print(f"\n🏥 Condiciones de salud:")
        for condicion, cantidad in condiciones.items():
            porcentaje = (cantidad / total) * 100
            nombre_legible = condicion.replace('_', ' ').title()
            print(f"   • {nombre_legible}: {cantidad:,} ({porcentaje:.1f}%)")
    
    def seed(self):
        """Seed para perfiles de salud basado en todos los usuarios existentes"""
        logger.info("Iniciando seeding de perfiles de salud...")
        print(f"\n🏥 Iniciando creación de perfiles de salud...")
        
        start_total = time.time()
        
        # 1. Obtener usuarios sin perfil de salud
        usuarios_sin_perfil = self.obtener_usuarios_sin_perfil()
        
        if not usuarios_sin_perfil:
            print("✅ Todos los usuarios ya tienen perfil de salud. No hay nada que hacer.")
            return
        
        # 2. Generar datos de perfiles en memoria
        perfiles_data = self.generar_perfiles_batch(usuarios_sin_perfil)
        
        # 3. Mostrar estadísticas antes de insertar
        self.mostrar_estadisticas(perfiles_data)
        
        # 4. Insertar usando bulk operations
        perfiles_creados = self.insertar_perfiles_bulk(perfiles_data)
        
        # 5. Resumen final
        total_elapsed = time.time() - start_total
        total_rate = perfiles_creados / total_elapsed if total_elapsed > 0 else 0
        
        print(f"\n🎉 ¡Seeding de perfiles de salud completado!")
        print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos")
        print(f"🚄 Velocidad promedio: {total_rate:.0f} perfiles/segundo")
        print(f"\n📊 Resumen final:")
        print(f"   • Perfiles creados: {perfiles_creados:,}")
        print(f"   • Total de usuarios con perfil: {perfiles_creados:,}")
        
        logger.info(f"Seeding de perfiles de salud completado:")
        logger.info(f"- Tiempo total: {total_elapsed:.2f}s")
        logger.info(f"- Perfiles creados: {perfiles_creados}")
        logger.info(f"- Velocidad: {total_rate:.0f} perfiles/seg")

if __name__ == "__main__":
    try:
        with HealthProfileSeeder() as seeder:
            seeder.create_tables()
            seeder.run(clear_first=True, table_names=['tbb_perfil_salud'])
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")