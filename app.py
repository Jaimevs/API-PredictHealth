# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine
from config.database import Base, engine
from config.settings import settings
from routes import (
    person,
    user,
    role,
    user_role,
    health_profile,
    smartwatch,
    heart_measurement,
    physical_activity,
    alert,
    auth,  # Autenticacion normal
    google_auth,  # Autenticacion con Google
    seeder  # Endpoints para seeders
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para monitoreo de salud y predicción de riesgos cardíacos con autenticación JWT y Google",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Manejo global de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Error de validación",
            "details": [
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"]
                }
                for error in exc.errors()
            ]
        }
    )

# Manejo global de errores HTTP
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        import traceback
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Error interno del servidor",
                "detail": str(exc),
                "traceback": traceback.format_exc()
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Error interno del servidor"}
        )

app.include_router(auth.router, prefix=settings.API_V1_STR)  # Autenticacion normal
app.include_router(google_auth.router, prefix=settings.API_V1_STR)  # Autenticacion Google Auth
app.include_router(person.router, prefix=settings.API_V1_STR)
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(role.router, prefix=settings.API_V1_STR)
app.include_router(user_role.router, prefix=settings.API_V1_STR)
app.include_router(health_profile.router, prefix=settings.API_V1_STR)
app.include_router(smartwatch.router, prefix=settings.API_V1_STR)
app.include_router(heart_measurement.router, prefix=settings.API_V1_STR)
app.include_router(physical_activity.router, prefix=settings.API_V1_STR)
app.include_router(alert.router, prefix=settings.API_V1_STR)
app.include_router(seeder.router, prefix=settings.API_V1_STR)  # Endpoints para seeders

@app.get("/")
def read_root():
    return {
        "message": "API Predict Health funcionando",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "auth_endpoints": {
            "normal_auth": f"{settings.API_V1_STR}/auth",
            "google_auth": f"{settings.API_V1_STR}/google-auth"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "message": "API funcionando correctamente",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "available_auth": ["email/password", "google"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=settings.DEBUG
    )