from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .routes import users, steam_games, favorite_games, auth, recommendations, rawg_games, games
from .database import engine, Base
import os

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar la aplicación FastAPI con metadata mejorada
app = FastAPI(
    title="Hidden Gem API",
    description="""
    # API para el sistema de recomendación de juegos indie 'Hidden Gem'
    
    Esta API proporciona funcionalidades para explorar y descubrir juegos indie menos conocidos 
    pero de gran calidad, basados en preferencias personales.
    
    ## Características principales
    
    * 🔐 **Autenticación**: Registro de usuarios, inicio de sesión y gestión de sesiones
    * 🎮 **Exploración de juegos**: Búsqueda, filtrado y visualización de juegos
    * ⭐ **Favoritos**: Guardar y gestionar juegos favoritos
    * 🎯 **Recomendaciones personalizadas**: Algoritmos que aprenden de tus preferencias
    * 🔍 **Integración con APIs externas**: Datos de RAWG y Steam
    
    ## Guía rápida
    
    1. Regístrate con `/api/auth/register`
    2. Inicia sesión con `/api/auth/login-json`
    3. Explora juegos con `/api/games`
    4. Añade favoritos con `/api/rawg/add-to-favorites`
    5. Obtén recomendaciones con `/api/recommendations/for-user/{user_id}`
    
    Para más información, consulte la documentación detallada de cada endpoint.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Equipo de Hidden Gem",
        "url": "https://example.com/contact/",
        "email": "contact@hidden-gem.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
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

# Configurar tags ordenados para la documentación
tags_metadata = [
    {
        "name": "auth",
        "description": "Operaciones de autenticación y gestión de usuarios.",
        "externalDocs": {
            "description": "Especificaciones de autenticación",
            "url": "https://example.com/auth-specs/",
        },
    },
    {
        "name": "users",
        "description": "Gestión de usuarios registrados.",
    },
    {
        "name": "games",
        "description": "Búsqueda y exploración de juegos de varias fuentes.",
    },
    {
        "name": "favorite-games",
        "description": "Gestión de juegos favoritos de usuarios.",
    },
    {
        "name": "recommendations",
        "description": "Sistema de recomendación personalizada basado en preferencias.",
    },
    {
        "name": "rawg-games",
        "description": "Integración con la API de RAWG para obtener información de juegos.",
    },
    {
        "name": "steam-games",
        "description": "Datos de juegos de Steam para recomendaciones.",
    },
]

# Personalizar el esquema OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
        terms_of_service=app.terms_of_service,
        contact=app.contact,
        license_info=app.license_info,
    )
    
    # Personalizar componentes del esquema OpenAPI
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Introduce el token JWT obtenido en el login",
        }
    }
    
    # Configurar seguridad global
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Añadir ejemplos adicionales
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                # Configurar la seguridad sólo para rutas protegidas
                if "login" not in path and "register" not in path and "check" not in path:
                    openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Incluir las rutas en la aplicación
app.include_router(users.router, prefix="/api")
app.include_router(steam_games.router, prefix="/api")
app.include_router(favorite_games.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(rawg_games.router, prefix="/api")
app.include_router(games.router, prefix="/api")  # Nuevas rutas de juegos

# Documentación personalizada usando HTML directo
@app.get("/api/custom-redoc", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc_html():
    html_content = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>{app.title} - Documentación API</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600&family=Poiret+One&display=swap" rel="stylesheet">
        <link rel="shortcut icon" href="/static/favicon.ico">
        <style>
          body {{
            margin: 0;
            padding: 0;
            font-family: 'Quicksand', sans-serif;
          }}
          redoc {{
            --theme-colors-primary-main: #b388ff;
          }}
        </style>
      </head>
      <body>
        <redoc spec-url="{app.openapi_url}"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
      </body>
    </html>
    """
    return html_content

# Servir archivos estáticos (opcional, para personalizar ReDoc)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Crear un favicon básico si no existe
if not os.path.exists("static/favicon.ico"):
    try:
        import base64
        favicon_data = b'AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A9v/7AOvgtgD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////APL/+ADw/vQF69+zQuvfsm7r37F4////AP///wD///8A////AP///wD///8A////AP///wD///8A////APD9+QHs4rgK697Bhurf0fDq3tD/6t/P2+vew7Dq38+y////AP///wD///8A////AP///wD///8A////AP///wD///8A697LPerd0fns5+T/9vPy//j29f/r39D/6t/T/+rfz//q3s1Z////AP///wD///8A////AP///wD///8A////AOvdzSbq3c//8e3r//39/f/39/f/+Pb1//f19P/z7+3/6+DS/+vezP/q3s9g////AP///wD///8A////AP///wD///8A////AP///wD///8A692+N+re0v/19PP/+ff3//n39//49/f/+Pf3//j39//49/f/+ff3/+vg1P/q3sYn////AP///wD///8A////AP///wD///8A////AP///wDq3suS7OXe//j4+P/49/f/+Pf3//j39//49/f/+Pf3//n39//u5+H/697Mav///wD///8A////AP///wD///8A////AP///wD///8A6t7LTOrezv/q4NT/7+nm//Xz8//08e//7eXh/+vh1v/q3cvs////AP///wD///8A////AP///wD///8A////AP///wD///8A6t3LaOrd0cXq3tHo6t7S/urezv/q3c3/6t3MqP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A////AP///wD///8A//8AAP//AAD//wAA//8AAP//AADn/wAAw/8AAIH/AAAAfwAAAD8AAAB/AAAAfwAAAP8AAAH/AAAD/wAA//8AAA=='
        favicon_bytes = base64.b64decode(favicon_data)
        with open("static/favicon.ico", "wb") as f:
            f.write(favicon_bytes)
    except Exception as e:
        print(f"No se pudo crear favicon: {e}")

# Ruta de inicio para redirigir a la documentación
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "¡Bienvenido a la API de Hidden Gem!",
        "documentation": [
            {"Standard API Docs": "/api/docs"},
            {"ReDoc": "/api/redoc"},
            {"Enhanced ReDoc": "/api/custom-redoc"}
        ],
        "version": app.version
    }

# Endpoint de estado para verificar el funcionamiento del servidor
@app.get("/api/health", tags=["system"], summary="Verificar estado del servidor")
async def health_check():
    """
    Endpoint para verificar que el servidor está funcionando correctamente.
    
    Returns:
        Un objeto con el estado del servidor y la versión de la API.
    """
    return {
        "status": "online",
        "version": app.version,
        "message": "¡API de Hidden Gem funcionando correctamente!"
    }

