# Sistema de Seeders - API PredictHealth

## Descripción General

El sistema de seeders permite poblar la base de datos con datos de prueba realistas para el desarrollo y testing de la API de salud predictiva. Incluye datos coherentes para usuarios, perfiles de salud, alertas, actividad física y mediciones cardíacas.

## Estructura del Sistema

### Seeders Disponibles (Orden de Ejecución)

1. **RoleSeeder** - Roles del sistema (ADMIN, USUARIO, MEDICO)
2. **PersonSeeder** - Personas de prueba con demografía realista
3. **UserSeeder** - Usuarios con autenticación y contraseñas hasheadas
4. **UserRoleSeeder** - Asignación de roles a usuarios
5. **SmartwatchSeeder** - Dispositivos smartwatch vinculados a usuarios
6. **HealthProfileSeeder** - Perfiles de salud médicos completos
7. **AlertsSeeder** - Alertas de salud con diferentes prioridades
8. **PhysicalActivitySeeder** - Datos de actividad física (90 días de historial)

### Archivos del Sistema

```
seeders/
├── __init__.py
├── base_seeder.py              # Clase base con funcionalidad común
├── main_seeder.py              # Orquestador principal
├── role_seeder.py              # Roles del sistema
├── person_seeder.py            # Demografía de personas
├── user_seeder.py              # Usuarios y autenticación
├── user_role_seeder.py         # Asignación de roles
├── smartwatch_seeder.py        # Dispositivos wearables
├── health_profile.py           # Perfiles médicos
├── alerts_seeder.py            # Alertas de salud
├── physical_activity_seeder.py # Actividad física
└── heart_measurement_seeder.py # Mediciones cardíacas
```

## Uso del Sistema

### 1. Ejecución Básica

```bash
# Ejecutar todos los seeders
python -m seeders.main_seeder

# Limpiar y volver a poblar
python -m seeders.main_seeder --clear

# Solo limpiar tablas sin poblar
python -m seeders.main_seeder --clear-only
```

### 2. Seeders Individuales

```bash
# Solo perfiles de salud
python -m seeders.main_seeder --health-only

# Seeder específico
python -m seeders.alerts_seeder --clear
python -m seeders.physical_activity_seeder --clear
```

### 3. Opciones Avanzadas

```bash
# Con confirmación para operaciones destructivas
python -m seeders.main_seeder --clear
# Preguntará: ¿Está seguro que desea continuar? (y/N)

# Limpieza completa sin confirmación adicional
python -m seeders.main_seeder --clear-only
```


