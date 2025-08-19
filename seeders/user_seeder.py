from .base_seeder import BaseSeeder
from models.user import User
from models.person import Person
from passlib.context import CryptContext
import logging
import random
from sqlalchemy import text
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

logger = logging.getLogger(__name__)

class UltraOptimizedUserSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        # Pre-hash algunas contraseñas comunes para reutilizar
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.common_passwords_hash = {}
        
        # Dominios y prefijos como listas para acceso más rápido
        self.dominios_email = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
            'email.com', 'correo.com', 'mail.com', 'live.com'
        ]
        
        self.prefijos_telefono = [
            '+52 555', '+52 449', '+52 33', '+52 81', '+52 222',
            '+52 664', '+52 668', '+52 614', '+52 844', '+52 477'
        ]
        
        # Mapeo de acentos compilado una sola vez
        self.acentos = str.maketrans({
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
        })
    
    def limpiar_texto_rapido(self, texto):
        """Versión optimizada de limpieza de texto"""
        return texto.lower().translate(self.acentos)
    
    def pre_hash_common_passwords(self, nombres_comunes):
        """Pre-hashea contraseñas comunes para reutilizar"""
        print("🔐 Pre-hasheando contraseñas comunes...")
        for nombre in nombres_comunes:
            if nombre not in self.common_passwords_hash:
                self.common_passwords_hash[nombre] = self.pwd_context.hash(f"{nombre}123")
    
    def seed_ultra_optimized(self):
        """Ultra optimizado usando SQL directo y técnicas avanzadas"""
        logger.info("Iniciando seeding ULTRA OPTIMIZADO de usuarios...")
        print(f"\n🚀 Iniciando creación ULTRA OPTIMIZADA de usuarios...")
        
        start_time = time.time()
        
        # PRIMERO: Contar exactamente cuántas personas necesitan usuario
        count_query = """
        SELECT COUNT(*) 
        FROM tbb_personas p 
        LEFT JOIN tbb_usuarios u ON p.ID = u.Persona_Id 
        WHERE p.Estatus = true AND u.Persona_Id IS NULL
        """
        
        result = self.db.execute(text(count_query))
        personas_sin_usuario = result.scalar()
        
        if personas_sin_usuario == 0:
            print("✅ Todas las personas ya tienen usuarios asignados.")
            return 0
        
        print(f"📊 Se encontraron {personas_sin_usuario:,} personas sin usuario")
        print(f"🚀 Generando {personas_sin_usuario:,} usuarios...")
        
        # MÉTODO 1: SQL DIRECTO - LA OPCIÓN MÁS RÁPIDA
        print("🔥 Usando inserción SQL directa...")
        ultra_fast_sql = """
        INSERT INTO tbb_usuarios (
            Persona_Id, 
            Nombre_Usuario, 
            Correo_Electronico, 
            Contrasena, 
            Numero_Telefonico_Movil, 
            Estatus
        )
        SELECT 
            p.ID,
            -- Generar username concatenando nombre + ID para garantizar unicidad
            CONCAT(
                LOWER(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        REPLACE(
                                            REPLACE(
                                                REPLACE(p.Nombre, 'á', 'a'), 
                                                'é', 'e'
                                            ), 
                                            'í', 'i'
                                        ), 
                                        'ó', 'o'
                                    ), 
                                    'ú', 'u'
                                ), 
                                'ñ', 'n'
                            ), 
                            'ü', 'u'
                        ), 
                        ' ', ''
                    )
                ),
                '.',
                LOWER(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        REPLACE(
                                            REPLACE(
                                                REPLACE(p.Primer_Apellido, 'á', 'a'), 
                                                'é', 'e'
                                            ), 
                                            'í', 'i'
                                        ), 
                                        'ó', 'o'
                                    ), 
                                    'ú', 'u'
                                ), 
                                'ñ', 'n'
                            ), 
                            'ü', 'u'
                        ), 
                        ' ', ''
                    )
                ),
                p.ID
            ) as username,
            
            -- Generar email con username + dominio
            CONCAT(
                LOWER(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        REPLACE(
                                            REPLACE(
                                                REPLACE(p.Nombre, 'á', 'a'), 
                                                'é', 'e'
                                            ), 
                                            'í', 'i'
                                        ), 
                                        'ó', 'o'
                                    ), 
                                    'ú', 'u'
                                ), 
                                'ñ', 'n'
                            ), 
                            'ü', 'u'
                        ), 
                        ' ', ''
                    )
                ),
                '.',
                LOWER(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        REPLACE(
                                            REPLACE(
                                                REPLACE(p.Primer_Apellido, 'á', 'a'), 
                                                'é', 'e'
                                            ), 
                                            'í', 'i'
                                        ), 
                                        'ó', 'o'
                                    ), 
                                    'ú', 'u'
                                ), 
                                'ñ', 'n'
                            ), 
                            'ü', 'u'
                        ), 
                        ' ', ''
                    )
                ),
                p.ID,
                '@gmail.com'
            ) as email,
            
            -- Contraseña hasheada simple (deberías cambiarla después)
            '$2b$12$LQv3c1yqBWVHxkd0LQ4YFODqNBUAyhyTLj3FeYBtEjSxWNT7cFvqm' as password_hash, -- = "password123"
            
            -- Teléfono con formato simple
            CONCAT('+52 555 ', LPAD(FLOOR(RAND() * 9999999), 7, '0')) as phone,
            
            true as status
            
        FROM tbb_personas p 
        LEFT JOIN tbb_usuarios u ON p.ID = u.Persona_Id 
        WHERE p.Estatus = true AND u.Persona_Id IS NULL;
        """
        
        try:
            result = self.db.execute(text(ultra_fast_sql))
            self.db.commit()
            
            usuarios_creados = result.rowcount
            elapsed_time = time.time() - start_time
            
            # Verificar que los números coincidan
            if usuarios_creados != personas_sin_usuario:
                print(f"⚠️  Advertencia: Se esperaban {personas_sin_usuario:,} usuarios, se crearon {usuarios_creados:,}")
            
            print(f"\n🎉 ¡ULTRA OPTIMIZACIÓN COMPLETADA!")
            print(f"⚡ Usuarios esperados: {personas_sin_usuario:,}")
            print(f"⚡ Usuarios creados: {usuarios_creados:,}")
            print(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
            
            if elapsed_time > 0:
                print(f"🚀 Velocidad: {usuarios_creados/elapsed_time:.0f} usuarios/segundo")
            
            print(f"\n📝 Información de acceso:")
            print(f"   • Contraseña por defecto: password123")
            print(f"   • Usuario: [nombre].[apellido][ID]")
            print(f"   • Email: [nombre].[apellido][ID]@gmail.com")
            
            return usuarios_creados
            
        except Exception as e:
            logger.error(f"Error en ultra optimización: {e}")
            print(f"❌ Error en SQL directo: {e}")
            print("🔄 Usando método alternativo...")
            return self.seed_parallel_fallback()
    
    def seed_parallel_fallback(self):
        """Método paralelo como fallback"""
        print("🔄 Iniciando método paralelo...")
        
        # Contar primero
        count_query = """
        SELECT COUNT(*) 
        FROM tbb_personas p 
        LEFT JOIN tbb_usuarios u ON p.ID = u.Persona_Id 
        WHERE p.Estatus = true AND u.Persona_Id IS NULL
        """
        
        result = self.db.execute(text(count_query))
        total_esperado = result.scalar()
        
        if total_esperado == 0:
            print("✅ No hay personas para procesar")
            return 0
        
        print(f"📊 Total esperado: {total_esperado:,}")
        
        # Obtener datos (sin LIMIT para obtener todos)
        query = """
        SELECT p.ID, p.Nombre, p.Primer_Apellido 
        FROM tbb_personas p 
        LEFT JOIN tbb_usuarios u ON p.ID = u.Persona_Id 
        WHERE p.Estatus = true AND u.Persona_Id IS NULL
        """
        
        result = self.db.execute(text(query))
        personas_data = result.fetchall()
        
        print(f"📊 Datos obtenidos: {len(personas_data):,} personas")
        print(f"📊 Procesando en paralelo...")
        
        # Verificar que coincidan los números
        if len(personas_data) != total_esperado:
            print(f"⚠️  Advertencia: Se esperaban {total_esperado:,}, se obtuvieron {len(personas_data):,}")
        
        # Pre-hashear contraseña común
        common_password = self.pwd_context.hash("password123")
        
        # Procesar en chunks grandes con bulk insert
        chunk_size = 5000
        total_creados = 0
        
        for i in range(0, len(personas_data), chunk_size):
            chunk = personas_data[i:i + chunk_size]
            users_data = []
            
            for persona_row in chunk:
                persona_id, nombre, apellido = persona_row
                
                # Generar datos rápido
                nombre_limpio = self.limpiar_texto_rapido(nombre)
                apellido_limpio = self.limpiar_texto_rapido(apellido)
                
                username = f"{nombre_limpio}.{apellido_limpio}{persona_id}"
                email = f"{username}@gmail.com"
                phone = f"+52 555 {random.randint(1000000, 9999999):07d}"
                
                users_data.append({
                    'Persona_Id': persona_id,
                    'Nombre_Usuario': username,
                    'Correo_Electronico': email,
                    'Contrasena': common_password,
                    'Numero_Telefonico_Movil': phone,
                    'Estatus': True
                })
            
            # Bulk insert
            try:
                self.db.bulk_insert_mappings(User, users_data)
                self.db.commit()
                total_creados += len(users_data)
                porcentaje = (total_creados / total_esperado) * 100
                print(f"📈 Progreso: {total_creados:,}/{total_esperado:,} usuarios creados ({porcentaje:.1f}%)")
                
            except Exception as e:
                logger.error(f"Error en chunk: {e}")
                self.db.rollback()
        
        # Verificación final
        if total_creados != total_esperado:
            print(f"⚠️  Advertencia: Se esperaban {total_esperado:,}, se crearon {total_creados:,}")
        
        return total_creados
    
    def seed(self):
        """Método principal que usa la ultra optimización"""
        return self.seed_ultra_optimized()

# Versión alternativa usando VALUES SQL para máxima velocidad
class SQLDirectUserSeeder(BaseSeeder):
    def seed_sql_values(self, limite=None):
        """Método usando VALUES SQL - ULTRA RÁPIDO"""
        print("🚀 Usando método SQL VALUES...")
        
        # Contar primero
        count_query = """
        SELECT COUNT(*) 
        FROM tbb_personas p 
        LEFT JOIN tbb_usuarios u ON p.ID = u.Persona_Id 
        WHERE p.Estatus = true AND u.Persona_Id IS NULL
        """
        
        result = self.db.execute(text(count_query))
        total_esperado = result.scalar()
        
        if total_esperado == 0:
            print("✅ No hay personas para procesar")
            return 0
        
        print(f"📊 Total esperado: {total_esperado:,}")
        
        # Obtener datos (aplicar límite si se especifica)
        limit_clause = f"LIMIT {limite}" if limite else ""
        query = f"""
        SELECT p.ID, p.Nombre, p.Primer_Apellido 
        FROM tbb_personas p 
        LEFT JOIN tbb_usuarios u ON p.ID = u.Persona_Id 
        WHERE p.Estatus = true AND u.Persona_Id IS NULL
        {limit_clause}
        """
        
        result = self.db.execute(text(query))
        personas_data = result.fetchall()
        
        total_a_procesar = len(personas_data)
        
        if limite:
            print(f"📊 Procesando {total_a_procesar:,} de {total_esperado:,} personas (limitado)")
        else:
            print(f"📊 Procesando {total_a_procesar:,} personas")
        
        if total_a_procesar == 0:
            print("✅ No hay personas para procesar")
            return 0
        
        # Construir SQL con VALUES
        values_parts = []
        for persona_id, nombre, apellido in personas_data:
            nombre_limpio = nombre.lower().translate(str.maketrans({
                'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                'ñ': 'n', 'ü': 'u', ' ': ''
            }))
            apellido_limpio = apellido.lower().translate(str.maketrans({
                'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                'ñ': 'n', 'ü': 'u', ' ': ''
            }))
            
            username = f"{nombre_limpio}.{apellido_limpio}{persona_id}"
            email = f"{username}@gmail.com"
            phone = f"+52 555 {random.randint(1000000, 9999999):07d}"
            
            values_parts.append(
                f"({persona_id}, '{username}', '{email}', "
                f"'$2b$12$LQv3c1yqBWVHxkd0LQ4YFODqNBUAyhyTLj3FeYBtEjSxWNT7cFvqm', "
                f"'{phone}', true)"
            )
        
        # Insertar por chunks para evitar límites de SQL
        chunk_size = 1000
        total_insertados = 0
        
        for i in range(0, len(values_parts), chunk_size):
            chunk_values = values_parts[i:i + chunk_size]
            
            sql = f"""
            INSERT INTO tbb_usuarios 
            (Persona_Id, Nombre_Usuario, Correo_Electronico, Contrasena, Numero_Telefonico_Movil, Estatus)
            VALUES {', '.join(chunk_values)}
            """
            
            try:
                result = self.db.execute(text(sql))
                self.db.commit()
                chunk_insertados = result.rowcount
                total_insertados += chunk_insertados
                
                porcentaje = (total_insertados / total_a_procesar) * 100
                print(f"📈 Progreso: {total_insertados:,}/{total_a_procesar:,} usuarios creados ({porcentaje:.1f}%)")
                
            except Exception as e:
                print(f"❌ Error en chunk: {e}")
                self.db.rollback()
        
        # Verificación final
        if total_insertados != total_a_procesar:
            print(f"⚠️  Advertencia: Se esperaban {total_a_procesar:,}, se insertaron {total_insertados:,}")
        
        return total_insertados

# Alias para mantener compatibilidad con imports existentes
UserSeeder = UltraOptimizedUserSeeder

if __name__ == "__main__":
    try:
        print("🚀 Selecciona el método de optimización:")
        print("1. Ultra Optimizado (SQL directo)")
        print("2. SQL VALUES (Alternativo)")
        
        opcion = input("Ingresa opción (1-2): ").strip()
        
        if opcion == "2":
            with SQLDirectUserSeeder() as seeder:
                seeder.create_tables()
                seeder.run(clear_first=True, table_names=['tbb_usuarios'])
                start = time.time()
                creados = seeder.seed_sql_values()
                elapsed = time.time() - start
                print(f"\n🎉 Completado en {elapsed:.2f}s - {creados/elapsed:.0f} usuarios/seg")
        else:
            with UltraOptimizedUserSeeder() as seeder:
                seeder.create_tables()
                seeder.run(clear_first=True, table_names=['tbb_usuarios'])
                
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error: {e}")
    finally:
        print("\n👋 Finalizando...")