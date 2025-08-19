from .base_seeder import BaseSeeder
from models.person import Person, GenderEnum
from datetime import date
import random
import logging

logger = logging.getLogger(__name__)

class PersonSeeder(BaseSeeder):
    def __init__(self):
        super().__init__()
        
        # Nombres masculinos
        self.nombres_masculinos = [
            'Juan', 'Carlos', 'Miguel', 'Roberto', 'David', 'José', 'Luis', 'Francisco', 
            'Antonio', 'Daniel', 'Fernando', 'Ricardo', 'Jorge', 'Manuel', 'Alberto',
            'Rafael', 'Pedro', 'Alejandro', 'Sergio', 'Andrés', 'Eduardo', 'Ramón',
            'Gabriel', 'Arturo', 'Héctor', 'Víctor', 'Óscar', 'Raúl', 'Javier',
            'Emilio', 'César', 'Ignacio', 'Mario', 'Pablo', 'Diego', 'Rodrigo',
            'Adrián', 'Iván', 'Rubén', 'Marcos', 'Nicolás', 'Sebastián', 'Leonardo',
            'Guillermo', 'Enrique', 'Felipe', 'Jaime', 'Gonzalo', 'Tomás', 'Cristian'
        ]
        
        # Nombres femeninos
        self.nombres_femeninos = [
            'María', 'Ana', 'Carmen', 'Sofia', 'Isabel', 'Patricia', 'Laura', 'Claudia',
            'Monica', 'Adriana', 'Lucia', 'Elena', 'Gabriela', 'Alejandra', 'Beatriz',
            'Silvia', 'Diana', 'Rosa', 'Teresa', 'Veronica', 'Martha', 'Dolores',
            'Gloria', 'Esperanza', 'Leticia', 'Cristina', 'Susana', 'Margarita', 'Alicia',
            'Fernanda', 'Valeria', 'Paola', 'Andrea', 'Carolina', 'Natalia', 'Daniela',
            'Rocío', 'Sandra', 'Victoria', 'Liliana', 'Norma', 'Eva', 'Karla',
            'Lorena', 'Yolanda', 'Cecilia', 'Marisol', 'Pilar', 'Angélica', 'Mónica'
        ]
        
        # Apellidos comunes
        self.apellidos = [
            'García', 'Martínez', 'López', 'González', 'Pérez', 'Rodríguez', 'Hernández',
            'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Rivera', 'Gómez', 'Díaz',
            'Cruz', 'Morales', 'Ortiz', 'Gutiérrez', 'Chávez', 'Ramos', 'Herrera',
            'Jiménez', 'Mendoza', 'Ruiz', 'Álvarez', 'Castillo', 'Moreno', 'Iglesias',
            'Castro', 'Ortega', 'Delgado', 'Guerrero', 'Medina', 'Vargas', 'Campos',
            'Vega', 'Romero', 'Aguilar', 'Serrano', 'Peña', 'Reyes', 'Molina',
            'Navarro', 'Muñoz', 'Rojas', 'Salazar', 'Silva', 'Contreras', 'Valdez'
        ]
    
    def obtener_cantidad_usuarios(self):
        """Solicitar al usuario la cantidad de personas a generar"""
        while True:
            try:
                print("\n" + "="*50)
                print("SEEDER DE PERSONAS")
                print("="*50)
                
                cantidad = input("¿Cuántas personas desea generar? (mínimo 1, máximo 100000): ")
                
                # Validar que sea un número
                cantidad = int(cantidad)
                
                # Validar rango
                if cantidad < 1:
                    print("❌ Error: La cantidad debe ser mayor a 0")
                    continue
                elif cantidad > 100000:
                    print("❌ Error: Por razones de rendimiento, el máximo es 10,000 personas")
                    continue
                
                # Confirmar con el usuario
                print(f"\n📊 Se generarán {cantidad:,} personas aleatorias")
                confirmacion = input("¿Desea continuar? (s/n): ").lower().strip()
                
                if confirmacion in ['s', 'si', 'sí', 'y', 'yes']:
                    return cantidad
                elif confirmacion in ['n', 'no']:
                    print("❌ Operación cancelada por el usuario")
                    return None
                else:
                    print("❌ Respuesta no válida. Por favor ingrese 's' para sí o 'n' para no")
                    continue
                    
            except ValueError:
                print("❌ Error: Por favor ingrese un número válido")
                continue
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada por el usuario")
                return None
    
    def generar_fecha_aleatoria(self):
        """Generar una fecha de nacimiento aleatoria entre 1950 y 2005"""
        año = random.randint(1950, 2005)
        mes = random.randint(1, 12)
        
        # Días según el mes
        dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # Verificar año bisiesto para febrero
        if mes == 2 and año % 4 == 0 and (año % 100 != 0 or año % 400 == 0):
            max_dia = 29
        else:
            max_dia = dias_por_mes[mes - 1]
        
        dia = random.randint(1, max_dia)
        return date(año, mes, dia)
    
    def generar_persona_aleatoria(self):
        """Generar datos de una persona aleatoria"""
        # Elegir género aleatoriamente
        genero = random.choice([GenderEnum.H, GenderEnum.M])
        
        # Elegir nombre según el género
        if genero == GenderEnum.H:
            nombre = random.choice(self.nombres_masculinos)
        else:
            nombre = random.choice(self.nombres_femeninos)
        
        # Elegir apellidos aleatoriamente - AMBOS OBLIGATORIOS
        primer_apellido = random.choice(self.apellidos)
        # Asegurar que el segundo apellido sea diferente al primero
        segundo_apellido = random.choice([ap for ap in self.apellidos if ap != primer_apellido])
        
        return {
            'Nombre': nombre,
            'Primer_Apellido': primer_apellido,
            'Segundo_Apellido': segundo_apellido,
            'Fecha_Nacimiento': self.generar_fecha_aleatoria(),
            'Genero': genero,
            'Estatus': True
        }
    
    def seed(self):
        """Seed dinámico para personas"""
        logger.info("Iniciando seeding dinámico de personas...")
        
        # Obtener cantidad del usuario
        cantidad = self.obtener_cantidad_usuarios()
        
        if cantidad is None:
            logger.info("Seeding cancelado por el usuario")
            return
        
        logger.info(f"Generando {cantidad:,} personas aleatorias...")
        print(f"\n🚀 Iniciando generación de {cantidad:,} personas...")
        
        personas_creadas = 0
        personas_duplicadas = 0
        
        # Determinar tamaño del lote basado en la cantidad
        if cantidad <= 100:
            lote_size = 10
        elif cantidad <= 1000:
            lote_size = 50
        else:
            lote_size = 100
        
        # Generar personas en lotes para mejor rendimiento
        for i in range(0, cantidad, lote_size):
            lote_actual = min(lote_size, cantidad - i)
            
            for j in range(lote_actual):
                persona_data = self.generar_persona_aleatoria()
                
                # Verificar si la persona ya existe (por nombre completo y fecha)
                existing_person = self.db.query(Person).filter(
                    Person.Nombre == persona_data['Nombre'],
                    Person.Primer_Apellido == persona_data['Primer_Apellido'],
                    Person.Segundo_Apellido == persona_data['Segundo_Apellido'],
                    Person.Fecha_Nacimiento == persona_data['Fecha_Nacimiento']
                ).first()
                
                if not existing_person:
                    persona = Person(**persona_data)
                    self.db.add(persona)
                    personas_creadas += 1
                    
                    # Mostrar progreso cada cierto número de personas
                    if personas_creadas % max(100, cantidad // 10) == 0:
                        porcentaje = (personas_creadas / cantidad) * 100
                        logger.info(f"Progreso: {personas_creadas:,}/{cantidad:,} personas creadas ({porcentaje:.1f}%)")
                        print(f"📈 Progreso: {personas_creadas:,}/{cantidad:,} ({porcentaje:.1f}%)")
                else:
                    personas_duplicadas += 1
            
            # Commit cada lote para mejor rendimiento
            try:
                self.db.commit()
            except Exception as e:
                logger.error(f"Error al hacer commit del lote: {e}")
                self.db.rollback()
                raise
        
        # Resumen final
        print(f"\n✅ Seeding completado exitosamente!")
        print(f"📊 Resumen:")
        print(f"   • Personas creadas: {personas_creadas:,}")
        print(f"   • Duplicados omitidos: {personas_duplicadas:,}")
        print(f"   • Total procesado: {(personas_creadas + personas_duplicadas):,}")
        
        logger.info(f"Seeding completado:")
        logger.info(f"- Personas creadas: {personas_creadas}")
        logger.info(f"- Duplicados omitidos: {personas_duplicadas}")
        logger.info(f"- Total procesado: {personas_creadas + personas_duplicadas}")

if __name__ == "__main__":
    try:
        with PersonSeeder() as seeder:
            seeder.create_tables()
            seeder.run(clear_first=True, table_names=['tbb_personas'])
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        logger.error(f"Error durante el seeding: {e}")
    finally:
        print("\n👋 Finalizando seeder...")