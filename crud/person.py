# crud/person.py
from sqlalchemy.orm import Session
from models.person import Person, GenderEnum
from typing import Optional
from datetime import datetime

def create_empty_person(db: Session) -> Person:
    """
    Crea una persona completamente vacía (solo con campos requeridos como NULL)
    Para vincular con el usuario, datos se llenan después
    """
    
    db_person = Person(
        Nombre=None,  # Intentar NULL
        Primer_Apellido=None,  # Intentar NULL
        Segundo_Apellido=None,  # Ya es opcional
        Fecha_Nacimiento=None,  # Intentar NULL
        Genero=None,  # Intentar NULL
        Estatus=True
    )
    
    try:
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person
    except Exception as e:
        # Si falla porque los campos son NOT NULL, usar valores "vacíos" especiales
        db.rollback()
        return create_person_with_empty_indicators(db)

def create_person_with_empty_indicators(db: Session) -> Person:
    """
    Crea persona con indicadores especiales de que está vacía
    Solo si los campos no permiten NULL
    """
    db_person = Person(
        Nombre="[PENDIENTE]",  # Indicador claro de que está vacío
        Primer_Apellido="[PENDIENTE]",  # Indicador claro de que está vacío
        Segundo_Apellido=None,  # Opcional, puede ser NULL
        Fecha_Nacimiento=None,  # Intentar NULL, si no se puede, usar fecha especial
        Genero=None,  # Intentar NULL
        Estatus=True
    )
    
    # Si Fecha_Nacimiento no permite NULL, usar fecha especial
    try:
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person
    except Exception:
        db.rollback()
        # Último recurso: usar valores especiales pero reconocibles
        db_person = Person(
            Nombre="[PENDIENTE]",
            Primer_Apellido="[PENDIENTE]", 
            Segundo_Apellido=None,
            Fecha_Nacimiento=datetime(1900, 1, 1).date(),  # Fecha claramente temporal
            Genero=GenderEnum.H,  # Valor temporal
            Estatus=True
        )
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person

def get_person(db: Session, person_id: int) -> Optional[Person]:
    """Obtiene una persona por ID"""
    return db.query(Person).filter(Person.ID == person_id).first()

def update_person(db: Session, person_id: int, person_data: dict) -> Optional[Person]:
    """Actualiza los datos de una persona"""
    db_person = db.query(Person).filter(Person.ID == person_id).first()
    if db_person:
        for field, value in person_data.items():
            if hasattr(db_person, field) and value is not None:
                # Convertir género a enum si es necesario
                if field == "Genero" and isinstance(value, str):
                    if value == "H":
                        value = GenderEnum.H
                    elif value == "M":
                        value = GenderEnum.M
                    elif value == "N/B":
                        value = GenderEnum.NB
                
                # Convertir fecha si es necesario
                if field == "Fecha_Nacimiento" and isinstance(value, str):
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        continue  # Saltar si el formato es incorrecto
                
                setattr(db_person, field, value)
        
        db.commit()
        db.refresh(db_person)
    return db_person

def is_person_empty(db: Session, person_id: int) -> bool:
    """Verifica si una persona tiene datos vacíos o pendientes"""
    person = get_person(db, person_id)
    if not person:
        return True
    
    # Verificar si los campos principales están vacíos o con indicadores
    return (
        person.Nombre in [None, "", "[PENDIENTE]"] or
        person.Primer_Apellido in [None, "", "[PENDIENTE]"] or
        person.Fecha_Nacimiento in [None, datetime(1900, 1, 1).date()]
    )