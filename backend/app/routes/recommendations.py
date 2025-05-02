from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.game import GameOut
from app.routes.auth import get_current_user
from app.services.recommendation_service import (
    get_similar_games,
    get_recommendations_for_user,
    get_hidden_gems
)

router = APIRouter()

@router.get("/for-user", response_model=List[GameOut])
async def recommendations_for_user(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera recomendaciones personalizadas para el usuario autenticado
    """
    games = get_recommendations_for_user(db, current_user, limit)
    return games

@router.get("/similar/{game_id}", response_model=List[GameOut])
async def similar_games(
    game_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve juegos similares al juego especificado
    """
    games = get_similar_games(db, game_id, limit)
    if not games and game_id > 0:
        raise HTTPException(status_code=404, detail="No se encontraron juegos similares")
    return games

@router.get("/hidden-gems", response_model=List[GameOut])
async def hidden_gems(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve una lista de joyas escondidas (juegos bien valorados pero poco conocidos).
    
    Este endpoint utiliza un algoritmo especializado para identificar juegos que tienen
    puntuaciones altas pero relativamente pocas reseñas o bajo reconocimiento general.
    Los resultados se filtran según las preferencias de precio del usuario actual.
    
    Parameters:
    - **limit**: Número máximo de resultados a devolver (por defecto: 10)
    
    Returns:
    - Lista de juegos que califican como "joyas escondidas"
    
    Algorithm:
    El algoritmo considera factores como:
    - Puntuación de críticos y usuarios
    - Número de reseñas (prefiriendo juegos con pocas reseñas)
    - Fecha de lanzamiento (dando preferencia a juegos más recientes)
    - Si el juego es indie
    - Precio (limitado por el precio máximo establecido por el usuario)
    
    Example response:
    ```json
    [
      {
        "id": 123,
        "title": "Inscryption",
        "description": "Un juego de cartas roguelike con elementos de escape room y horror psicológico",
        "genres": "Card Game,Indie,Roguelike,Horror",
        "url": "https://store.steampowered.com/app/1092790/Inscryption/",
        "price": 19.99,
        "image_url": "https://cdn.akamai.steamstatic.com/steam/apps/1092790/header.jpg",
        "score": 4.8,
        "tags": "Cartas,Terror,Indie,Roguelike",
        "is_indie": true
      },
      ...
    ]
    ```
    """
    games = get_hidden_gems(db, limit)
    return games