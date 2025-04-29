from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routes import auth, games, scraper

# Crear instancia de FastAPI
app = FastAPI(
    title="HiddenGem API",
    description="API para descubrir juegos indie poco conocidos",
    version="0.1.0"
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

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bienvenido a la API de HiddenGem"}

# Lógica para ejecutar con uvicorn si es __main__
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
