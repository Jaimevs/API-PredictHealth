from .base_seeder import BaseSeeder
from models.user_role import UserRole
from models.user import User
from models.role import Role
import logging
import random

logger = logging.getLogger(__name__)

class UserRoleSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Configuración de distribución de roles
        self.config_roles = {
            'ADMIN': {
                'cantidad': 2,
                'descripcion': 'Administradores del sistema'
            },
            'MEDICO': {
                'cantidad': 2,
                'descripcion': 'Médicos/Doctores'
            },
            'USUARIO': {
                'descripcion': 'Usuarios regulares (resto de usuarios)'
            }
        }
    
    def obtener_configuracion_roles(self):
        """Permitir al usuario configurar la cantidad de cada rol (opcional)"""
        print("\n" + "="*60)
        print("CONFIGURACIÓN DE ROLES")
        print("="*60)
        print("Configuración actual:")
        
        for role_name, config in self.config_roles.items():
            if 'cantidad' in config:
                print(f"  • {role_name}: {config['cantidad']} usuarios - {config['descripcion']}")
            else:
                print(f"  • {role_name}: Resto de usuarios - {config['descripcion']}")
        
        print(f"\n¿Desea modificar esta configuración? (s/n): ", end="")
        modificar = input().lower().strip()
        
        if modificar in ['s', 'si', 'sí', 'y', 'yes']:
            return self.configurar_roles_personalizado()
        
        return self.config_roles
    
    def configurar_roles_personalizado(self):
        """Permitir configuración personalizada de roles"""
        nueva_config = {}
        
        print("\n📝 Configuración personalizada:")
        
        # Configurar ADMIN
        while True:
            try:
                cantidad_admin = input("¿Cuántos ADMIN desea? (mínimo 1): ")
                cantidad_admin = int(cantidad_admin)
                if cantidad_admin >= 1:
                    nueva_config['ADMIN'] = {
                        'cantidad': cantidad_admin,
                        'descripcion': 'Administradores del sistema'
                    }
                    break
                else:
                    print("❌ Debe haber al menos 1 administrador")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        # Configurar MEDICO
        while True:
            try:
                cantidad_medico = input("¿Cuántos MEDICO desea? (mínimo 1): ")
                cantidad_medico = int(cantidad_medico)
                if cantidad_medico >= 1:
                    nueva_config['MEDICO'] = {
                        'cantidad': cantidad_medico,
                        'descripcion': 'Médicos/Doctores'
                    }
                    break
                else:
                    print("❌ Debe haber al menos 1 médico")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        # USUARIO siempre es el resto
        nueva_config['USUARIO'] = {
            'descripcion': 'Usuarios regulares (resto de usuarios)'
        }
        
        return nueva_config
    
    def validar_roles_disponibles(self, roles_db):
        """Validar que existan los roles necesarios en la base de datos"""
        roles_existentes = {role.Nombre for role in roles_db}
        roles_necesarios = set(self.config_roles.keys())
        
        roles_faltantes = roles_necesarios - roles_existentes
        
        if roles_faltantes:
            error_msg = f"❌ Faltan los siguientes roles en la base de datos: {', '.join(roles_faltantes)}"
            logger.error(error_msg)
            print(error_msg)
            print("💡 Ejecute primero RoleSeeder para crear los roles necesarios")
            return False
        
        return True
    
    def seleccionar_usuarios_para_rol(self, usuarios_disponibles, cantidad, rol_nombre):
        """Seleccionar usuarios para un rol específico"""
        if cantidad >= len(usuarios_disponibles):
            return usuarios_disponibles.copy()
        
        # Para ADMIN, preferir usuarios con nombres que sugieran administración
        if rol_nombre == 'ADMIN':
            usuarios_admin = []
            nombres_admin = ['admin', 'administrator', 'root', 'super']
            
            for usuario in usuarios_disponibles:
                for nombre_admin in nombres_admin:
                    if nombre_admin in usuario.Nombre_Usuario.lower() or nombre_admin in usuario.Correo_Electronico.lower():
                        usuarios_admin.append(usuario)
                        break
            
            # Si encontramos usuarios "admin", usarlos primero
            if usuarios_admin:
                seleccionados = usuarios_admin[:cantidad]
                # Si necesitamos más, completar aleatoriamente
                if len(seleccionados) < cantidad:
                    restantes = [u for u in usuarios_disponibles if u not in seleccionados]
                    seleccionados.extend(random.sample(restantes, cantidad - len(seleccionados)))
                return seleccionados
        
        # Para MEDICO, preferir usuarios con nombres que sugieran medicina
        elif rol_nombre == 'MEDICO':
            usuarios_medico = []
            nombres_medico = ['dr', 'doctor', 'medico', 'dra']
            
            for usuario in usuarios_disponibles:
                for nombre_medico in nombres_medico:
                    if nombre_medico in usuario.Nombre_Usuario.lower() or nombre_medico in usuario.Correo_Electronico.lower():
                        usuarios_medico.append(usuario)
                        break
            
            # Si encontramos usuarios "doctor", usarlos primero
            if usuarios_medico:
                seleccionados = usuarios_medico[:cantidad]
                # Si necesitamos más, completar aleatoriamente
                if len(seleccionados) < cantidad:
                    restantes = [u for u in usuarios_disponibles if u not in seleccionados]
                    seleccionados.extend(random.sample(restantes, cantidad - len(seleccionados)))
                return seleccionados
        
        # Selección aleatoria para otros casos
        return random.sample(usuarios_disponibles, cantidad)
    
    def seed(self):
        """Seed dinámico para asignación de roles a usuarios"""
        logger.info("Iniciando seeding de asignación de roles...")
        print(f"\n🔄 Iniciando asignación de roles a usuarios...")
        
        # Obtener usuarios y roles
        users = self.db.query(User).filter(User.Estatus == True).all()
        roles_db = self.db.query(Role).all()
        
        if not users:
            error_msg = "❌ No hay usuarios en la base de datos. Ejecute primero UserSeeder."
            logger.error(error_msg)
            print(error_msg)
            return
        
        if not roles_db:
            error_msg = "❌ No hay roles en la base de datos. Ejecute primero RoleSeeder."
            logger.error(error_msg)
            print(error_msg)
            return
        
        # Validar que existan los roles necesarios
        if not self.validar_roles_disponibles(roles_db):
            return
        
        total_usuarios = len(users)
        print(f"📊 Total de usuarios encontrados: {total_usuarios:,}")
        
        # Obtener configuración de roles
        config_roles = self.obtener_configuracion_roles()
        
        # Validar que haya suficientes usuarios
        usuarios_necesarios = sum(config.get('cantidad', 0) for config in config_roles.values() if 'cantidad' in config)
        
        if usuarios_necesarios > total_usuarios:
            error_msg = f"❌ No hay suficientes usuarios. Necesarios: {usuarios_necesarios}, Disponibles: {total_usuarios}"
            logger.error(error_msg)
            print(error_msg)
            return
        
        # Crear diccionario de roles por nombre
        roles_dict = {role.Nombre: role for role in roles_db}
        
        # Lista de usuarios disponibles para asignar
        usuarios_disponibles = users.copy()
        random.shuffle(usuarios_disponibles)  # Mezclar para distribución aleatoria
        
        asignaciones_creadas = 0
        asignaciones_existentes = 0
        
        print(f"\n🎯 Distribución de roles:")
        
        # Procesar cada tipo de rol
        for rol_nombre, config in config_roles.items():
            role = roles_dict[rol_nombre]
            
            if 'cantidad' in config:
                # Roles con cantidad fija (ADMIN, MEDICO)
                cantidad = config['cantidad']
                usuarios_seleccionados = self.seleccionar_usuarios_para_rol(
                    usuarios_disponibles, cantidad, rol_nombre
                )
                
                # Remover usuarios seleccionados de la lista disponible
                for usuario in usuarios_seleccionados:
                    if usuario in usuarios_disponibles:
                        usuarios_disponibles.remove(usuario)
                
                print(f"   • {rol_nombre}: {len(usuarios_seleccionados)} usuarios")
                
            else:
                # USUARIO - resto de usuarios
                usuarios_seleccionados = usuarios_disponibles.copy()
                usuarios_disponibles = []  # Ya no quedan disponibles
                
                print(f"   • {rol_nombre}: {len(usuarios_seleccionados)} usuarios (resto)")
            
            # Crear asignaciones para este rol
            for usuario in usuarios_seleccionados:
                # Verificar si la asignación ya existe
                existing_assignment = self.db.query(UserRole).filter(
                    UserRole.Usuario_ID == usuario.ID,
                    UserRole.Rol_ID == role.ID
                ).first()
                
                if not existing_assignment:
                    user_role = UserRole(
                        Usuario_ID=usuario.ID,
                        Rol_ID=role.ID,
                        Estatus=True
                    )
                    self.db.add(user_role)
                    asignaciones_creadas += 1
                    logger.info(f"Asignación creada: {usuario.Nombre_Usuario} -> {role.Nombre}")
                else:
                    asignaciones_existentes += 1
                    logger.info(f"Asignación ya existe: {usuario.Nombre_Usuario} -> {role.Nombre}")
        
        # Commit de todas las asignaciones
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Error al hacer commit: {e}")
            self.db.rollback()
            raise
        
        # Resumen final
        total_asignaciones = asignaciones_creadas + asignaciones_existentes
        
        print(f"\n✅ Asignación de roles completada exitosamente!")
        print(f"📊 Resumen:")
        print(f"   • Asignaciones creadas: {asignaciones_creadas:,}")
        print(f"   • Asignaciones ya existentes: {asignaciones_existentes:,}")
        print(f"   • Total de asignaciones: {total_asignaciones:,}")
        print(f"   • Usuarios procesados: {total_usuarios:,}")
        
        logger.info(f"Seeding de asignación de roles completado:")
        logger.info(f"- Asignaciones creadas: {asignaciones_creadas}")
        logger.info(f"- Asignaciones existentes: {asignaciones_existentes}")
        logger.info(f"- Total procesado: {total_asignaciones}")

if __name__ == "__main__":
    try:
        with UserRoleSeeder() as seeder:
            seeder.create_tables()
            seeder.run(clear_first=True, table_names=['tbd_usuarios_roles'])
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")