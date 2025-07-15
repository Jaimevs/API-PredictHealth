from sqlalchemy.orm import Session
from models.person import Person

def get_person(db: Session, person_id: int):
    return db.query(Person).filter(Person.ID == person_id).first()

def get_persons(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Person).filter(Person.Estatus == True).offset(skip).limit(limit).all()

def create_person(db: Session, person_data: dict):
    db_person = Person(
        Nombre=person_data["Nombre"],
        Primer_Apellido=person_data["Primer_Apellido"],
        Segundo_Apellido=person_data.get("Segundo_Apellido"),
        Fecha_Nacimiento=person_data["Fecha_Nacimiento"],
        Genero=person_data["Genero"],
        Estatus=person_data.get("Estatus", True)
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def update_person(db: Session, person_id: int, person_data: dict):
    db_person = db.query(Person).filter(Person.ID == person_id).first()
    if db_person:
        for key, value in person_data.items():
            setattr(db_person, key, value)
        db.commit()
        db.refresh(db_person)
    return db_person

def delete_person(db: Session, person_id: int):
    db_person = db.query(Person).filter(Person.ID == person_id).first()
    if db_person:
        db_person.Estatus = False
        db.commit()
        db.refresh(db_person)
    return db_person