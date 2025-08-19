from .base_seeder import BaseSeeder
from models.user_role import UserRole
from models.user import User
from models.role import Role
import logging
import random
from sqlalchemy import text
import time

logger = logging.getLogger(__name__)

class UltraOptimizedUserRoleSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Configuración de distribución de roles
        self.config_roles = {
            'ADMIN': {
                'cantidad': 2,
                'descripcion': 'Administradores del sistema',
                'prioridad_nombres': ['admin', 'administrator', 'root', 'super']
            },
            'MEDICO': {
                'cantidad': 2,
                'descripcion': 'Médicos/Doctores',
                'prioridad_nombres': ['dr', 'doctor', 'medico', 'dra']
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
                        'descripcion': 'Administradores del sistema',
                        'prioridad_nombres': ['admin', 'administrator', 'root', 'super']
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
                        'descripcion': 'Médicos/Doctores',
                        'prioridad_nombres': ['dr', 'doctor', 'medico', 'dra']
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
    
    def seed_ultra_optimized(self):
        """Ultra optimización usando SQL directo"""
        logger.info("Iniciando seeding ULTRA OPTIMIZADO de roles...")
        print(f"\n🚀 Iniciando asignación ULTRA OPTIMIZADA de roles...")
        
        start_time = time.time()
        
        # 1. VALIDACIONES RÁPIDAS CON QUERIES OPTIMIZADAS
        print("🔍 Validando datos...")
        
        # Contar usuarios y roles de una vez
        validation_query = """
        SELECT 
            (SELECT COUNT(*) FROM tbb_usuarios WHERE Estatus = true) as total_usuarios,
            (SELECT COUNT(*) FROM tbc_roles) as total_roles,
            (SELECT COUNT(*) FROM tbc_roles WHERE Nombre IN ('ADMIN', 'MEDICO', 'USUARIO')) as roles_necesarios
        """
        
        result = self.db.execute(text(validation_query))
        stats = result.fetchone()
        
        total_usuarios = stats[0]
        total_roles = stats[1]
        roles_necesarios = stats[2]
        
        if total_usuarios == 0:
            print("❌ No hay usuarios en la base de datos. Ejecute primero UserSeeder.")
            return 0
        
        if total_roles == 0:
            print("❌ No hay roles en la base de datos. Ejecute primero RoleSeeder.")
            return 0
        
        if roles_necesarios < 3:
            print("❌ Faltan roles necesarios (ADMIN, MEDICO, USUARIO)")
            return 0
        
        print(f"📊 Total de usuarios: {total_usuarios:,}")
        print(f"📊 Roles disponibles: {total_roles}")
        
        # 2. OBTENER CONFIGURACIÓN
        config_roles = self.obtener_configuracion_roles()
        
        # Validar suficientes usuarios
        usuarios_necesarios = sum(config.get('cantidad', 0) for config in config_roles.values() if 'cantidad' in config)
        
        if usuarios_necesarios > total_usuarios:
            print(f"❌ No hay suficientes usuarios. Necesarios: {usuarios_necesarios}, Disponibles: {total_usuarios}")
            return 0
        
        # 3. MÉTODO SQL DIRECTO - SÚPER RÁPIDO
        print("🔥 Usando asignación SQL directa...")
        
        # Obtener IDs de roles
        roles_query = "SELECT ID, Nombre FROM tbc_roles WHERE Nombre IN ('ADMIN', 'MEDICO', 'USUARIO')"
        roles_result = self.db.execute(text(roles_query))
        roles_dict = {nombre: id_rol for id_rol, nombre in roles_result}
        
        admin_role_id = roles_dict['ADMIN']
        medico_role_id = roles_dict['MEDICO']
        usuario_role_id = roles_dict['USUARIO']
        
        # Eliminar asignaciones existentes si se especifica
        print("🧹 Limpiando asignaciones anteriores...")
        self.db.execute(text("DELETE FROM tbd_usuarios_roles"))
        self.db.commit()
        
        total_asignaciones = 0
        
        # 4. ASIGNAR ADMINS (SQL directo con prioridad por nombres)
        admin_cantidad = config_roles['ADMIN']['cantidad']
        nombres_admin = config_roles['ADMIN']['prioridad_nombres']
        
        # Buscar usuarios que parezcan admins primero
        admin_priority_sql = f"""
        INSERT INTO tbd_usuarios_roles (Usuario_ID, Rol_ID, Estatus, Fecha_Registro)
        SELECT u.ID, {admin_role_id}, true, NOW()
        FROM tbb_usuarios u
        WHERE u.Estatus = true 
        AND (
            {' OR '.join([f"LOWER(u.Nombre_Usuario) LIKE '%{nombre}%' OR LOWER(u.Correo_Electronico) LIKE '%{nombre}%'" for nombre in nombres_admin])}
        )
        ORDER BY RAND()
        LIMIT {admin_cantidad}
        """
        
        result = self.db.execute(text(admin_priority_sql))
        admins_asignados = result.rowcount
        self.db.commit()
        
        # Si necesitamos más admins, tomar usuarios aleatorios
        if admins_asignados < admin_cantidad:
            admin_random_sql = f"""
            INSERT INTO tbd_usuarios_roles (Usuario_ID, Rol_ID, Estatus, Fecha_Registro)
            SELECT u.ID, {admin_role_id}, true, NOW()
            FROM tbb_usuarios u
            WHERE u.Estatus = true 
            AND u.ID NOT IN (SELECT Usuario_ID FROM tbd_usuarios_roles)
            ORDER BY RAND()
            LIMIT {admin_cantidad - admins_asignados}
            """
            
            result = self.db.execute(text(admin_random_sql))
            admins_asignados += result.rowcount
            self.db.commit()
        
        total_asignaciones += admins_asignados
        print(f"✅ ADMIN: {admins_asignados} usuarios asignados")
        
        # 5. ASIGNAR MÉDICOS (SQL directo con prioridad por nombres)
        medico_cantidad = config_roles['MEDICO']['cantidad']
        nombres_medico = config_roles['MEDICO']['prioridad_nombres']
        
        # Buscar usuarios que parezcan médicos primero
        medico_priority_sql = f"""
        INSERT INTO tbd_usuarios_roles (Usuario_ID, Rol_ID, Estatus, Fecha_Registro)
        SELECT u.ID, {medico_role_id}, true, NOW()
        FROM tbb_usuarios u
        WHERE u.Estatus = true 
        AND u.ID NOT IN (SELECT Usuario_ID FROM tbd_usuarios_roles)
        AND (
            {' OR '.join([f"LOWER(u.Nombre_Usuario) LIKE '%{nombre}%' OR LOWER(u.Correo_Electronico) LIKE '%{nombre}%'" for nombre in nombres_medico])}
        )
        ORDER BY RAND()
        LIMIT {medico_cantidad}
        """
        
        result = self.db.execute(text(medico_priority_sql))
        medicos_asignados = result.rowcount
        self.db.commit()
        
        # Si necesitamos más médicos, tomar usuarios aleatorios
        if medicos_asignados < medico_cantidad:
            medico_random_sql = f"""
            INSERT INTO tbd_usuarios_roles (Usuario_ID, Rol_ID, Estatus, Fecha_Registro)
            SELECT u.ID, {medico_role_id}, true, NOW()
            FROM tbb_usuarios u
            WHERE u.Estatus = true 
            AND u.ID NOT IN (SELECT Usuario_ID FROM tbd_usuarios_roles)
            ORDER BY RAND()
            LIMIT {medico_cantidad - medicos_asignados}
            """
            
            result = self.db.execute(text(medico_random_sql))
            medicos_asignados += result.rowcount
            self.db.commit()
        
        total_asignaciones += medicos_asignados
        print(f"✅ MEDICO: {medicos_asignados} usuarios asignados")
        
        # 6. ASIGNAR RESTO COMO USUARIOS (SQL directo)
        usuario_sql = f"""
        INSERT INTO tbd_usuarios_roles (Usuario_ID, Rol_ID, Estatus, Fecha_Registro)
        SELECT u.ID, {usuario_role_id}, true, NOW()
        FROM tbb_usuarios u
        WHERE u.Estatus = true 
        AND u.ID NOT IN (SELECT Usuario_ID FROM tbd_usuarios_roles)
        """
        
        result = self.db.execute(text(usuario_sql))
        usuarios_asignados = result.rowcount
        self.db.commit()
        
        total_asignaciones += usuarios_asignados
        print(f"✅ USUARIO: {usuarios_asignados} usuarios asignados")
        
        elapsed_time = time.time() - start_time
        
        # 7. RESUMEN FINAL
        print(f"\n🎉 ¡ULTRA OPTIMIZACIÓN COMPLETADA!")
        print(f"⚡ Total de asignaciones: {total_asignaciones:,}")
        print(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
        
        if elapsed_time > 0:
            print(f"🚀 Velocidad: {total_asignaciones/elapsed_time:.0f} asignaciones/segundo")
        
        print(f"\n📊 Distribución final:")
        print(f"   • ADMIN: {admins_asignados} usuarios")
        print(f"   • MEDICO: {medicos_asignados} usuarios")
        print(f"   • USUARIO: {usuarios_asignados} usuarios")
        
        logger.info(f"Seeding ultra optimizado completado: {total_asignaciones} asignaciones en {elapsed_time:.2f}s")
        
        return total_asignaciones
    
    def seed_fallback_optimized(self, config_roles_param=None):
        """Método optimizado usando bulk insert como fallback"""
        print("🔄 Usando método bulk insert optimizado...")
        
        # Usar configuración pasada como parámetro para evitar preguntar dos veces
        if config_roles_param is None:
            config_roles = self.obtener_configuracion_roles()
        else:
            config_roles = config_roles_param
        
        # Obtener todos los datos necesarios en queries optimizadas
        users_query = """
        SELECT u.ID, u.Nombre_Usuario, u.Correo_Electronico
        FROM tbb_usuarios u 
        LEFT JOIN tbd_usuarios_roles ur ON u.ID = ur.Usuario_ID
        WHERE u.Estatus = true AND ur.Usuario_ID IS NULL
        """
        
        users_result = self.db.execute(text(users_query))
        usuarios_data = users_result.fetchall()
        
        if not usuarios_data:
            print("✅ Todos los usuarios ya tienen roles asignados")
            return 0
        
        # Obtener roles
        roles_query = "SELECT ID, Nombre FROM tbc_roles WHERE Nombre IN ('ADMIN', 'MEDICO', 'USUARIO')"
        roles_result = self.db.execute(text(roles_query))
        roles_dict = {nombre: id_rol for id_rol, nombre in roles_result}
        
        # Preparar asignaciones
        asignaciones_data = []
        usuarios_disponibles = list(usuarios_data)
        random.shuffle(usuarios_disponibles)
        
        # Asignar ADMIN con prioridad por nombres
        admin_cantidad = config_roles['ADMIN']['cantidad']
        nombres_admin = config_roles['ADMIN']['prioridad_nombres']
        
        # Buscar usuarios que parezcan admins
        admin_usuarios = []
        usuarios_restantes = []
        
        for user_id, username, email in usuarios_disponibles:
            es_admin = any(nombre in username.lower() or nombre in email.lower() 
                          for nombre in nombres_admin)
            
            if es_admin and len(admin_usuarios) < admin_cantidad:
                admin_usuarios.append((user_id, username, email))
            else:
                usuarios_restantes.append((user_id, username, email))
        
        # Completar admins si es necesario
        while len(admin_usuarios) < admin_cantidad and usuarios_restantes:
            admin_usuarios.append(usuarios_restantes.pop(0))
        
        # Crear asignaciones para admins
        for user_id, username, email in admin_usuarios:
            asignaciones_data.append({
                'Usuario_ID': user_id,
                'Rol_ID': roles_dict['ADMIN'],
                'Estatus': True
            })
        
        # Asignar MEDICO con prioridad por nombres
        medico_cantidad = config_roles['MEDICO']['cantidad']
        nombres_medico = config_roles['MEDICO']['prioridad_nombres']
        
        medico_usuarios = []
        usuarios_finales = []
        
        for user_id, username, email in usuarios_restantes:
            es_medico = any(nombre in username.lower() or nombre in email.lower() 
                           for nombre in nombres_medico)
            
            if es_medico and len(medico_usuarios) < medico_cantidad:
                medico_usuarios.append((user_id, username, email))
            else:
                usuarios_finales.append((user_id, username, email))
        
        # Completar médicos si es necesario
        while len(medico_usuarios) < medico_cantidad and usuarios_finales:
            medico_usuarios.append(usuarios_finales.pop(0))
        
        # Crear asignaciones para médicos
        for user_id, username, email in medico_usuarios:
            asignaciones_data.append({
                'Usuario_ID': user_id,
                'Rol_ID': roles_dict['MEDICO'],
                'Estatus': True
            })
        
        # Asignar resto como USUARIO
        for user_id, username, email in usuarios_finales:
            asignaciones_data.append({
                'Usuario_ID': user_id,
                'Rol_ID': roles_dict['USUARIO'],
                'Estatus': True
            })
        
        # Bulk insert
        if asignaciones_data:
            self.db.bulk_insert_mappings(UserRole, asignaciones_data)
            self.db.commit()
            
            print(f"✅ ADMIN: {len(admin_usuarios)} usuarios asignados")
            print(f"✅ MEDICO: {len(medico_usuarios)} usuarios asignados")
            print(f"✅ USUARIO: {len(usuarios_finales)} usuarios asignados")
        
        return len(asignaciones_data)
    
    def seed(self):
        """Método principal que usa ultra optimización"""
        try:
            return self.seed_ultra_optimized()
        except Exception as e:
            logger.error(f"Error en ultra optimización: {e}")
            print(f"⚠️  Error en SQL directo: {e}")
            print("🔄 Usando método alternativo...")
            
            # Obtener la configuración una sola vez para pasarla al fallback
            config_roles = self.obtener_configuracion_roles()
            return self.seed_fallback_optimized(config_roles)

# Alias para mantener compatibilidad
UserRoleSeeder = UltraOptimizedUserRoleSeeder

if __name__ == "__main__":
    try:
        start = time.time()
        with UltraOptimizedUserRoleSeeder() as seeder:
            seeder.create_tables()
            seeder.run(clear_first=True, table_names=['tbd_usuarios_roles'])
        
        elapsed = time.time() - start
        print(f"\n¡Proceso completado en {elapsed:.2f} segundos!")
        
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")