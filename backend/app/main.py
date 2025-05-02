from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routes import auth, games, scraper, recommendations, rawg
import logging
logging.basicConfig(level=logging.INFO)

# Crear instancia de FastAPI con metadatos mejorados
app = FastAPI(
    title="HiddenGem API",
    description="API para descubrir juegos indie poco conocidos y joyas escondidas en el mundo de los videojuegos.",
    version="0.1.0",
    redoc_url="/redoc",
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {
            "name": "Autenticación",
            "description": "Operaciones relacionadas con registro y autenticación de usuarios."
        },
        {
            "name": "Juegos",
            "description": "Endpoints para gestionar y consultar información de juegos en nuestra base de datos."
        },
        {
            "name": "Scraper",
            "description": "Funcionalidades para obtener datos de juegos desde Steam mediante web scraping."
        },
        {
            "name": "Recommendations",
            "description": "Sistema de recomendaciones personalizado basado en preferencias de usuario y algoritmos de descubrimiento."
        },
        {
            "name": "RAWG API",
            "description": "Integración con la API de RAWG para obtener información detallada sobre videojuegos."
        },
        {
            "name": "Root",
            "description": "Punto de entrada principal para la API."
        }
    ],
    contact={
        "name": "Equipo HiddenGem",
        "url": "https://github.com/tu_usuario/hidden-gem",
        "email": "contacto@hiddengem.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://hiddengem.com/terms/",
)

# Configurar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de los diferentes módulos
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(games.router, prefix="/api/games", tags=["Juegos"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["Scraper"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(rawg.router, prefix="/api/rawg", tags=["RAWG API"])

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz que proporciona información básica sobre la API de HiddenGem.
    
    Returns:
        dict: Un mensaje de bienvenida con enlaces a la documentación.
    """
    return {
        "message": "Bienvenido a la API de HiddenGem",
        "documentation": {
            "Redoc": "/redoc",
            "Swagger UI": "/docs"
        },
        "version": "0.1.0"
    }

# Lógica para ejecutar con uvicorn si es __main__
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
