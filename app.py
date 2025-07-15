from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from config.database import Base, engine
from routes import (
    person,
    user,
    role,
    user_role,
    health_profile,
    smartwatch,
    heart_measurement,
    physical_activity,
    alert
)

app = FastAPI(
    title="API Predict Health",
    description="API para monitoreo de salud y predicción de riesgos cardíacos",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(person.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(user_role.router)
app.include_router(health_profile.router)
app.include_router(smartwatch.router)
app.include_router(heart_measurement.router)
app.include_router(physical_activity.router)
app.include_router(alert.router)

@app.get("/")
def read_root():
    return {"message": "API Predict Health esta funcionando"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)