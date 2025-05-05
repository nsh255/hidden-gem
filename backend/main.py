from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, auth, favorite_games, recommendations, steam_games, games, rawg_games
import uvicorn

app = FastAPI(title="Hidden Gem API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug print of available routes
@app.on_event("startup")
async def startup_event():
    print("Available routes:")
    for route in app.routes:
        print(f"{route.methods} {route.path}")

# Include routers - making sure all have the same prefix structure
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(favorite_games.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(steam_games.router, prefix="/api")
app.include_router(games.router, prefix="/api")
app.include_router(rawg_games.router, prefix="/api")

# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Welcome to Hidden Gem API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
