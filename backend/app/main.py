from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.staticfiles import StaticFiles
from .routes import users, steam_games, favorite_games, rawg_games, recommendations, auth
from .database import engine
from . import models
from .config import settings

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Crear un router principal con prefijo /api
api_router = APIRouter(prefix="/api")

# Definir tags para agrupar endpoints en la documentación
tags_metadata = [
    {
        "name": "auth",
        "description": "Autenticación de usuarios. Login y generación de tokens JWT.",
        "externalDocs": {
            "description": "Más información sobre autenticación",
            "url": "https://github.com/nsh255/hidden-gem/wiki/authentication",
        },
    },
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
    {
        "name": "recommendations",
        "description": "Sistema de recomendación de juegos indies basado en preferencias del usuario y análisis de géneros favoritos.",
        "externalDocs": {
            "description": "Algoritmo de recomendación",
            "url": "https://github.com/yourusername/hidden-gem/wiki/recommendation-algorithm",
        },
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
    * Obtener recomendaciones personalizadas basadas en preferencias
    
    ## Autenticación
    
    La API utiliza autenticación basada en JWT (JSON Web Tokens). Para acceder a endpoints protegidos:
    
    1. Obtén un token usando el endpoint `/api/auth/login` o `/api/auth/login-json`
    2. Incluye el token en el encabezado de tus peticiones: `Authorization: Bearer {token}`
    
    Ejemplo de respuesta de login:
    ```json
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "nick": "username",
        "email": "user@example.com"
      }
    }
    ```
    
    Todos los endpoints están disponibles bajo el prefijo `/api`.
    
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

# Incluir routers en el router principal
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(steam_games.router)
api_router.include_router(favorite_games.router)
api_router.include_router(rawg_games.router)
api_router.include_router(recommendations.router)

# Incluir el router principal en la aplicación
app.include_router(api_router)

@app.get("/", tags=["root"])
def read_root():
    return {
        "message": "Bienvenido a la API de Hidden Gem",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "api_prefix": "/api"
    }

@app.get("/health", status_code=200, tags=["health"])
def health_check():
    return {"status": "ok"}
