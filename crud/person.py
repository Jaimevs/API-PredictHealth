from sqlalchemy.orm import Session
from models.person import Person, GenderEnum
from typing import Optional
from datetime import datetime

def create_empty_person(db: Session) -> Person:
    """
    Crea una persona vacía (solo con valores mínimos requeridos)
    Para vincular con el usuario, datos se llenan después
    """
    # Crear persona con valores mínimos requeridos por la BD
    db_person = Person(
        Nombre="", 
        Primer_Apellido="", 
        Segundo_Apellido=None, 
        Fecha_Nacimiento=datetime(1900, 1, 1).date(),  
        Genero=GenderEnum.H, 
        Estatus=True
    )
    
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    
    return db_person

def get_person(db: Session, person_id: int) -> Optional[Person]:
    """Obtiene una persona por ID"""
    return db.query(Person).filter(Person.ID == person_id).first()

def get_persons(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de personas"""
    return db.query(Person).filter(Person.Estatus == True).offset(skip).limit(limit).all()

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
    """Verifica si una persona tiene datos vacíos"""
    person = get_person(db, person_id)
    if not person:
        return True
    
    # Verificar si los campos principales están vacíos
    return (
        person.Nombre == "" and 
        person.Primer_Apellido == "" and
        person.Fecha_Nacimiento == datetime(1900, 1, 1).date()
    )