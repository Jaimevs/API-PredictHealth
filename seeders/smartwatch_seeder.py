from .base_seeder import BaseSeeder
from models.smartwatch import Smartwatch
from models.user import User
import logging
import random
import time
import string
from datetime import datetime, timedelta
from sqlalchemy import text

logger = logging.getLogger(__name__)

class SmartwatchSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Marcas y modelos reales de smartwatches
        self.marcas_modelos = {
            'Apple': [
                'Apple Watch Series 9', 'Apple Watch SE (2nd gen)', 'Apple Watch Ultra 2',
                'Apple Watch Series 8', 'Apple Watch Series 7', 'Apple Watch SE'
            ],
            'Samsung': [
                'Galaxy Watch6', 'Galaxy Watch6 Classic', 'Galaxy Watch5',
                'Galaxy Watch4', 'Galaxy Watch Active2', 'Galaxy Watch3'
            ],
            'Garmin': [
                'Venu 3', 'Forerunner 965', 'Epix Pro', 'Fenix 7',
                'Vivoactive 5', 'Venu 2', 'Forerunner 255'
            ],
            'Fitbit': [
                'Sense 2', 'Versa 4', 'Charge 5', 'Luxe',
                'Inspire 3', 'Versa 3', 'Sense'
            ],
            'Huawei': [
                'Watch GT 4', 'Watch D2', 'Watch Ultimate',
                'Watch GT 3', 'Watch Fit 2', 'Watch GT Runner'
            ],
            'Xiaomi': [
                'Mi Watch S3', 'Redmi Watch 4', 'Mi Band 8',
                'Redmi Watch 3', 'Mi Watch Revolve', 'Mi Band 7'
            ]
        }
        
        # Distribución de marcas (porcentajes aproximados del mercado)
        self.distribucion_marcas = [
            ('Apple', 0.35),     # 35%
            ('Samsung', 0.25),   # 25%
            ('Garmin', 0.15),    # 15%
            ('Fitbit', 0.10),    # 10%
            ('Huawei', 0.08),    # 8%
            ('Xiaomi', 0.07),    # 7%
        ]
    
    def generar_numero_serie(self, marca):
        """Generar número de serie realista según la marca"""
        if marca == 'Apple':
            # Formato Apple: XXXXXXXXXXXXXX (14 caracteres alfanuméricos)
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
        elif marca == 'Samsung':
            # Formato Samsung: RF8XXXXXXXXX (RF8 + 9 caracteres)
            return 'RF8' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        elif marca == 'Garmin':
            # Formato Garmin: 3xxxxxxxxxx (3 + 10 dígitos)
            return '3' + ''.join(random.choices(string.digits, k=10))
        elif marca == 'Fitbit':
            # Formato Fitbit: FB + 8 caracteres alfanuméricos
            return 'FB' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        elif marca == 'Huawei':
            # Formato Huawei: HW + 10 caracteres alfanuméricos
            return 'HW' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        elif marca == 'Xiaomi':
            # Formato Xiaomi: MI + 8 dígitos
            return 'MI' + ''.join(random.choices(string.digits, k=8))
        else:
            # Formato genérico
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    def seleccionar_marca_modelo(self):
        """Seleccionar marca y modelo basado en distribución de mercado"""
        rand = random.random()
        acumulado = 0
        
        for marca, probabilidad in self.distribucion_marcas:
            acumulado += probabilidad
            if rand <= acumulado:
                modelos = self.marcas_modelos[marca]
                modelo = random.choice(modelos)
                return marca, modelo
        
        # Fallback (no debería llegar aquí)
        return 'Apple', 'Apple Watch Series 9'
    
    def generar_fecha_vinculacion(self):
        """Generar fecha de vinculación realista (últimos 2 años)"""
        # Fecha entre hace 2 años y ahora
        fecha_inicio = datetime.now() - timedelta(days=730)
        fecha_fin = datetime.now()
        
        # Generar fecha aleatoria en ese rango
        tiempo_aleatorio = random.random() * (fecha_fin - fecha_inicio).total_seconds()
        fecha_vinculacion = fecha_inicio + timedelta(seconds=tiempo_aleatorio)
        
        return fecha_vinculacion
    
    def obtener_usuarios_sin_smartwatch(self):
        """Obtener usuarios que no tienen smartwatch"""
        print("🔍 Verificando usuarios sin smartwatch...")
        start_time = time.time()
        
        # Usar ORM en lugar de SQL directo para mejor compatibilidad
        usuarios_sin_smartwatch = self.db.query(User).filter(
            User.Estatus == True,
            ~User.ID.in_(
                self.db.query(Smartwatch.Usuario_ID).filter(
                    Smartwatch.Estatus == True
                )
            )
        ).all()
        
        elapsed = time.time() - start_time
        print(f"✅ Verificación completada en {elapsed:.2f} segundos")
        print(f"📊 Usuarios sin smartwatch encontrados: {len(usuarios_sin_smartwatch):,}")
        
        return usuarios_sin_smartwatch
    
    def generar_smartwatches_para_todos(self, usuarios_sin_smartwatch):
        """Generar smartwatches para TODOS los usuarios sin smartwatch"""
        print(f"🔧 Generando smartwatches para TODOS los usuarios sin smartwatch...")
        start_time = time.time()
        
        smartwatches_data = []
        numeros_serie_usados = set()
        
        # Obtener números de serie existentes para evitar duplicados
        existing_series = self.db.query(Smartwatch.Numero_serie).all()
        numeros_serie_usados.update([serie[0] for serie in existing_series])
        
        for i, usuario in enumerate(usuarios_sin_smartwatch):
            # Seleccionar marca y modelo
            marca, modelo = self.seleccionar_marca_modelo()
            
            # Generar número de serie único
            while True:
                numero_serie = self.generar_numero_serie(marca)
                if numero_serie not in numeros_serie_usados:
                    numeros_serie_usados.add(numero_serie)
                    break
            
            # Generar fecha de vinculación
            fecha_vinculacion = self.generar_fecha_vinculacion()
            
            # Decidir si está activo (95% activos)
            activo = random.random() < 0.95
            
            smartwatch_data = {
                'Usuario_ID': usuario.ID,
                'Marca': marca,
                'Modelo': modelo,
                'Numero_serie': numero_serie,
                'Fecha_vinculacion': fecha_vinculacion,
                'Activo': activo,
                'Estatus': True,
                'Fecha_Registro': datetime.now()
            }
            
            smartwatches_data.append(smartwatch_data)
            
            # Mostrar progreso cada 1000 usuarios
            if (i + 1) % 1000 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"📈 Procesados: {i + 1:,}/{len(usuarios_sin_smartwatch):,} "
                      f"({rate:.0f} usuarios/seg)")
        
        elapsed = time.time() - start_time
        
        print(f"✅ Generación completada en {elapsed:.2f} segundos")
        print(f"📊 Smartwatches generados: {len(smartwatches_data):,}")
        
        return smartwatches_data
    
    def insertar_smartwatches_bulk(self, smartwatches_data, batch_size=1000):
        """Insertar smartwatches usando bulk insert"""
        total_smartwatches = len(smartwatches_data)
        if total_smartwatches == 0:
            print("📱 No hay smartwatches para insertar.")
            return 0
        
        print(f"💾 Insertando {total_smartwatches:,} smartwatches en lotes de {batch_size:,}...")
        
        start_time = time.time()
        smartwatches_insertados = 0
        
        for i in range(0, total_smartwatches, batch_size):
            batch = smartwatches_data[i:i + batch_size]
            
            try:
                self.db.bulk_insert_mappings(Smartwatch, batch)
                self.db.commit()
                
                smartwatches_insertados += len(batch)
                
                # Mostrar progreso
                elapsed = time.time() - start_time
                if elapsed > 0:
                    rate = smartwatches_insertados / elapsed
                    porcentaje = (smartwatches_insertados / total_smartwatches) * 100
                    
                    print(f"📈 Insertados: {smartwatches_insertados:,}/{total_smartwatches:,} "
                          f"({porcentaje:.1f}%) - {rate:.0f} smartwatches/seg")
                
            except Exception as e:
                logger.error(f"Error insertando lote {i//batch_size + 1}: {e}")
                self.db.rollback()
                raise
        
        elapsed = time.time() - start_time
        final_rate = smartwatches_insertados / elapsed if elapsed > 0 else 0
        
        print(f"✅ Inserción completada en {elapsed:.2f} segundos ({final_rate:.0f} smartwatches/seg)")
        
        return smartwatches_insertados
    
    def mostrar_estadisticas(self, smartwatches_data):
        """Mostrar estadísticas de los smartwatches generados"""
        if not smartwatches_data:
            print("📊 No hay datos para mostrar estadísticas.")
            return
        
        print(f"\n📈 Estadísticas de smartwatches generados:")
        
        # Contar por marca
        marcas = {}
        activos = 0
        
        for smartwatch in smartwatches_data:
            marca = smartwatch['Marca']
            marcas[marca] = marcas.get(marca, 0) + 1
            
            if smartwatch['Activo']:
                activos += 1
        
        total = len(smartwatches_data)
        
        print(f"📱 Distribución por marca:")
        for marca, cantidad in sorted(marcas.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (cantidad / total) * 100
            print(f"   • {marca}: {cantidad:,} ({porcentaje:.1f}%)")
        
        print(f"\n🔋 Estado de activación:")
        porcentaje_activos = (activos / total) * 100
        print(f"   • Activos: {activos:,} ({porcentaje_activos:.1f}%)")
        print(f"   • Inactivos: {total - activos:,} ({100 - porcentaje_activos:.1f}%)")
    
    def mostrar_confirmacion(self, total_usuarios, usuarios_sin_smartwatch):
        """Mostrar confirmación antes de proceder"""
        print(f"\n" + "="*60)
        print("CONFIRMACIÓN DE ASIGNACIÓN DE SMARTWATCHES")
        print("="*60)
        print(f"📊 Total de usuarios en el sistema: {total_usuarios:,}")
        print(f"📱 Usuarios sin smartwatch: {len(usuarios_sin_smartwatch):,}")
        print(f"🎯 Smartwatches a crear: {len(usuarios_sin_smartwatch):,}")
        
        if len(usuarios_sin_smartwatch) == 0:
            print(f"✅ Todos los usuarios ya tienen smartwatch asignado.")
            return False
        
        print(f"\n¿Desea proceder con la creación de {len(usuarios_sin_smartwatch):,} smartwatches? (s/n): ", end="")
        respuesta = input().lower().strip()
        
        return respuesta in ['s', 'si', 'sí', 'y', 'yes']
    
    def seed(self):
        """Seed para asignar smartwatch a TODOS los usuarios"""
        logger.info("Iniciando seeding de smartwatches...")
        print(f"\n📱 Iniciando asignación de smartwatches a TODOS los usuarios...")
        
        start_total = time.time()
        
        # 1. Obtener todos los usuarios activos
        all_users = self.db.query(User).filter(User.Estatus == True).all()
        
        if not all_users:
            error_msg = "❌ No hay usuarios en la base de datos. Ejecute primero UserSeeder."
            logger.error(error_msg)
            print(error_msg)
            return
        
        print(f"📊 Total de usuarios encontrados: {len(all_users):,}")
        
        # 2. Obtener usuarios que no tienen smartwatch
        usuarios_sin_smartwatch = self.obtener_usuarios_sin_smartwatch()
        
        # 3. Mostrar confirmación
        if not self.mostrar_confirmacion(len(all_users), usuarios_sin_smartwatch):
            print("❌ Operación cancelada por el usuario.")
            return
        
        # 4. Generar smartwatches para todos los usuarios sin smartwatch
        smartwatches_data = self.generar_smartwatches_para_todos(usuarios_sin_smartwatch)
        
        # 5. Mostrar estadísticas antes de insertar
        self.mostrar_estadisticas(smartwatches_data)
        
        # 6. Insertar usando bulk operations
        smartwatches_creados = self.insertar_smartwatches_bulk(smartwatches_data)
        
        # 7. Verificar resultado final
        total_smartwatches_final = self.db.query(Smartwatch).filter(Smartwatch.Estatus == True).count()
        total_usuarios_final = len(all_users)
        
        # 8. Resumen final
        total_elapsed = time.time() - start_total
        total_rate = smartwatches_creados / total_elapsed if total_elapsed > 0 else 0
        
        print(f"\n🎉 ¡Seeding de smartwatches completado!")
        print(f"⏱️  Tiempo total: {total_elapsed:.2f} segundos")
        print(f"🚄 Velocidad promedio: {total_rate:.0f} smartwatches/segundo")
        print(f"\n📊 Resumen final:")
        print(f"   • Smartwatches creados: {smartwatches_creados:,}")
        print(f"   • Total de usuarios: {total_usuarios_final:,}")
        print(f"   • Total de smartwatches: {total_smartwatches_final:,}")
        print(f"   • Cobertura: {(total_smartwatches_final/total_usuarios_final)*100:.1f}%")
        
        # Verificar si todos los usuarios tienen smartwatch
        if total_smartwatches_final == total_usuarios_final:
            print(f"✅ ¡Perfecto! Todos los usuarios tienen smartwatch asignado.")
        else:
            print(f"⚠️  Aún hay usuarios sin smartwatch: {total_usuarios_final - total_smartwatches_final}")
        
        logger.info(f"Seeding de smartwatches completado:")
        logger.info(f"- Tiempo total: {total_elapsed:.2f}s")
        logger.info(f"- Smartwatches creados: {smartwatches_creados}")
        logger.info(f"- Velocidad: {total_rate:.0f} smartwatches/seg")
        logger.info(f"- Cobertura: {(total_smartwatches_final/total_usuarios_final)*100:.1f}%")

if __name__ == "__main__":
    try:
        with SmartwatchSeeder() as seeder:
            seeder.create_tables()
            seeder.run(clear_first=True, table_names=['tbb_smartwatches'])
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")