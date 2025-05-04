from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.staticfiles import StaticFiles
from .routes import users, steam_games, favorite_games, auth, recommendations, rawg_games, games
from .database import engine, Base
import os

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="Hidden Gem API",
    description="""
    API para el sistema de recomendación de juegos indie 'Hidden Gem'.
    
    Esta API proporciona funcionalidades para:
    * Registro y autenticación de usuarios
    * Búsqueda y exploración de juegos
    * Gestión de juegos favoritos
    * Recomendaciones personalizadas
    
    Para más información, consulte la documentación detallada de cada endpoint.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
origins = [
    "http://localhost:4200",  # Frontend de Angular
    "http://localhost:8000",  # Backend de desarrollo
    # Añadir aquí otros orígenes permitidos en producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas en la aplicación
app.include_router(users.router, prefix="/api")
app.include_router(steam_games.router, prefix="/api")
app.include_router(favorite_games.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(rawg_games.router, prefix="/api")
app.include_router(games.router, prefix="/api")  # Nuevas rutas de juegos

# Mejorar ReDoc con estilos personalizados
@app.get("/api/custom-redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico",
        with_google_fonts=True,
        redoc_html_attrs={"style": "typography.fontSize=16px"}
    )

# Servir archivos estáticos (opcional, para personalizar ReDoc)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta de inicio para redirigir a la documentación
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Bienvenido a la API de Hidden Gem. Visite /api/docs o /api/redoc para ver la documentación."}

