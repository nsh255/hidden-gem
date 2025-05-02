from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.staticfiles import StaticFiles
from .routes import users, steam_games, favorite_games, rawg_games
from .database import engine
from . import models
from .config import settings

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Definir tags para agrupar endpoints en la documentación
tags_metadata = [
    {
        "name": "users",
        "description": "Operaciones con usuarios. Registro, consulta y manejo de perfiles.",
    },
    {
        "name": "steam-games",
        "description": "Gestión de juegos scrapeados de Steam para recomendaciones.",
    },
    {
        "name": "favorite-games",
        "description": "Gestión de juegos favoritos de usuarios provenientes de RAWG.",
    },
    {
        "name": "rawg-games",
        "description": "Interacción con la API de RAWG para buscar y obtener información de juegos.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.PROJECT_VERSION,
    description="""
    API para recomendaciones de juegos indie.
    
    Esta API permite:
    * Gestionar usuarios y sus preferencias de juegos
    * Acceder a juegos de Steam para recomendaciones
    * Permitir a los usuarios marcar sus juegos favoritos
    * Interactuar con la API de RAWG para descubrir nuevos juegos
    
    La API usa PostgreSQL como base de datos y está construida con FastAPI.
    """,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Hidden Gem Team",
        "url": "https://github.com/nsh255/hidden-gem",
        "email": "nsh255@inlumine.ual.es",
    },
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(users.router)
app.include_router(steam_games.router)
app.include_router(favorite_games.router)
app.include_router(rawg_games.router)

@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "Bienvenido a la API de Hidden Gem",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", status_code=200, tags=["health"])
def health_check():
    return {"status": "ok"}
