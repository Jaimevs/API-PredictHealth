from .base_seeder import BaseSeeder
from models.user import User
from models.person import Person
from passlib.context import CryptContext
import logging
import random

logger = logging.getLogger(__name__)

class UserSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Dominios de correo comunes
        self.dominios_email = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
            'email.com', 'correo.com', 'mail.com', 'live.com'
        ]
        
        # Prefijos para números telefónicos mexicanos
        self.prefijos_telefono = [
            '+52 555', '+52 449', '+52 33', '+52 81', '+52 222',
            '+52 664', '+52 668', '+52 614', '+52 844', '+52 477'
        ]
    
    def get_password_hash(self, password):
        """Hashear contraseña usando bcrypt"""
        return self.pwd_context.hash(password)
    
    def generar_nombre_usuario(self, persona):
        """Generar nombre de usuario basado en los datos de la persona"""
        nombre = persona.Nombre.lower()
        primer_apellido = persona.Primer_Apellido.lower()
        
        # Remover acentos y caracteres especiales
        nombre = self.limpiar_texto(nombre)
        primer_apellido = self.limpiar_texto(primer_apellido)
        
        # Diferentes formatos de usuario
        formatos = [
            f"{nombre}.{primer_apellido}",
            f"{nombre}{primer_apellido}",
            f"{nombre[0]}{primer_apellido}",
            f"{nombre}{primer_apellido[0]}",
            f"{nombre}.{primer_apellido}{random.randint(1, 999)}"
        ]
        
        return random.choice(formatos)
    
    def limpiar_texto(self, texto):
        """Limpiar texto removiendo acentos y caracteres especiales"""
        # Mapa de caracteres con acentos a sin acentos
        acentos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
        }
        
        for con_acento, sin_acento in acentos.items():
            texto = texto.replace(con_acento, sin_acento)
        
        return texto
    
    def generar_correo_electronico(self, persona, nombre_usuario):
        """Generar correo electrónico basado en el nombre de usuario"""
        dominio = random.choice(self.dominios_email)
        return f"{nombre_usuario}@{dominio}"
    
    def generar_telefono(self):
        """Generar número telefónico mexicano aleatorio"""
        prefijo = random.choice(self.prefijos_telefono)
        numero = random.randint(1000000, 9999999)
        return f"{prefijo} {numero:07d}"
    
    def generar_contrasena_simple(self, persona):
        """Generar contraseña simple basada en el nombre"""
        nombre = self.limpiar_texto(persona.Nombre.lower())
        return f"{nombre}123"
    
    def seed(self):
        """Seed para usuarios basado en todas las personas existentes"""
        logger.info("Iniciando seeding de usuarios...")
        print(f"\n🔄 Iniciando creación de usuarios...")
        
        # Obtener TODAS las personas de la base de datos
        personas = self.db.query(Person).filter(Person.Estatus == True).all()
        
        if not personas:
            error_msg = "❌ No hay personas en la base de datos. Ejecute primero PersonSeeder."
            logger.error(error_msg)
            print(error_msg)
            return
        
        total_personas = len(personas)
        print(f"📊 Se encontraron {total_personas:,} personas en la base de datos")
        print(f"🚀 Generando usuarios para todas las personas...")
        
        usuarios_creados = 0
        usuarios_existentes = 0
        nombres_usuario_usados = set()
        correos_usados = set()
        
        # Obtener usuarios existentes para evitar duplicados
        usuarios_existentes_db = self.db.query(User).all()
        for user in usuarios_existentes_db:
            nombres_usuario_usados.add(user.Nombre_Usuario)
            correos_usados.add(user.Correo_Electronico)
        
        # Procesar en lotes para mejor rendimiento
        lote_size = 100
        for i in range(0, total_personas, lote_size):
            lote_actual = min(lote_size, total_personas - i)
            lote_personas = personas[i:i + lote_actual]
            
            for persona in lote_personas:
                # Verificar si ya existe un usuario para esta persona
                existing_user = self.db.query(User).filter(
                    User.Persona_Id == persona.ID
                ).first()
                
                if existing_user:
                    usuarios_existentes += 1
                    continue
                
                # Generar nombre de usuario único
                intentos = 0
                while intentos < 10:  # Máximo 10 intentos
                    nombre_usuario = self.generar_nombre_usuario(persona)
                    if nombre_usuario not in nombres_usuario_usados:
                        nombres_usuario_usados.add(nombre_usuario)
                        break
                    intentos += 1
                else:
                    # Si no se pudo generar nombre único, usar ID
                    nombre_usuario = f"{self.limpiar_texto(persona.Nombre.lower())}{persona.ID}"
                    nombres_usuario_usados.add(nombre_usuario)
                
                # Generar correo único
                intentos = 0
                while intentos < 10:  # Máximo 10 intentos
                    correo = self.generar_correo_electronico(persona, nombre_usuario)
                    if correo not in correos_usados:
                        correos_usados.add(correo)
                        break
                    intentos += 1
                    # Modificar nombre de usuario para generar correo diferente
                    nombre_usuario = f"{nombre_usuario}{random.randint(1, 99)}"
                else:
                    # Si no se pudo generar correo único, usar ID
                    correo = f"{nombre_usuario}{persona.ID}@gmail.com"
                    correos_usados.add(correo)
                
                # Crear datos del usuario
                user_data = {
                    'Persona_Id': persona.ID,
                    'Nombre_Usuario': nombre_usuario,
                    'Correo_Electronico': correo,
                    'Contrasena': self.get_password_hash(self.generar_contrasena_simple(persona)),
                    'Numero_Telefonico_Movil': self.generar_telefono(),
                    'Estatus': True
                }
                
                # Crear usuario
                usuario = User(**user_data)
                self.db.add(usuario)
                usuarios_creados += 1
                
                # Mostrar progreso
                if usuarios_creados % max(100, total_personas // 10) == 0:
                    porcentaje = ((i + len(lote_personas)) / total_personas) * 100
                    logger.info(f"Progreso: {usuarios_creados:,} usuarios creados ({porcentaje:.1f}%)")
                    print(f"📈 Progreso: {usuarios_creados:,}/{total_personas:,} usuarios creados ({porcentaje:.1f}%)")
            
            # Commit cada lote
            try:
                self.db.commit()
            except Exception as e:
                logger.error(f"Error al hacer commit del lote: {e}")
                self.db.rollback()
                raise
        
        # Resumen final
        total_procesado = usuarios_creados + usuarios_existentes
        
        print(f"\n✅ Seeding de usuarios completado exitosamente!")
        print(f"📊 Resumen:")
        print(f"   • Usuarios creados: {usuarios_creados:,}")
        print(f"   • Usuarios ya existentes: {usuarios_existentes:,}")
        print(f"   • Total de personas procesadas: {total_procesado:,}")
        print(f"   • Total de personas en DB: {total_personas:,}")
        
        if usuarios_creados > 0:
            print(f"\n📝 Información de acceso:")
            print(f"   • Contraseñas generadas: [nombre]123 (ej: juan123)")
            print(f"   • Usuarios: [nombre].[apellido] o variaciones")
        
        logger.info(f"Seeding de usuarios completado:")
        logger.info(f"- Usuarios creados: {usuarios_creados}")
        logger.info(f"- Usuarios existentes: {usuarios_existentes}")
        logger.info(f"- Total procesado: {total_procesado}")

if __name__ == "__main__":
    try:
        with UserSeeder() as seeder:
            seeder.create_tables()
            seeder.run(clear_first=True, table_names=['tbb_usuarios'])
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")