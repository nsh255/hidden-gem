from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rawg_api import search_games, get_game_details, get_genres
from app.models.user import User
from app.routes.auth import get_current_user

router = APIRouter()

@router.get("/search")
async def search_rawg_games(
    genres: Optional[List[str]] = Query(None), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca juegos en la API de RAWG con filtros opcionales
    """
    try:
        games = search_games(genres=genres)
        return {"games": games}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar juegos: {str(e)}")

@router.get("/genres")
async def list_genres(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la lista de géneros disponibles en RAWG
    """
    try:
        genres = get_genres()
        return {"genres": genres}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener géneros: {str(e)}")

@router.get("/details/{game_id}")
async def get_rawg_game_details(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene detalles completos de un juego específico desde RAWG.
    
    Este endpoint realiza una consulta a la API de RAWG para obtener información
    detallada sobre un juego específico usando su ID único.
    
    Parameters:
    - **game_id**: Identificador único del juego en la base de datos de RAWG
    
    Returns:
    - Objeto con todos los detalles del juego incluyendo título, descripción,
      imágenes, géneros, plataformas, puntuaciones, etc.
    
    Raises:
    - HTTPException 404: Si el juego no se encuentra
    - HTTPException 500: Si ocurre un error al comunicarse con la API de RAWG
    
    Example response:
    ```json
    {
      "id": 3498,
      "name": "Grand Theft Auto V",
      "description": "Una descripción detallada del juego...",
      "metacritic": 92,
      "released": "2013-09-17",
      "background_image": "https://media.rawg.io/media/games/456/456dea5e1c7e3cd07060c14e96612001.jpg",
      "genres": [{"id": 4, "name": "Action"}, {"id": 3, "name": "Adventure"}],
      "platforms": [{"platform": {"id": 4, "name": "PC"}}],
      "ratings": [...],
      "developers": [...],
      "publishers": [...]
    }
    ```
    """
    try:
        game = get_game_details(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return game
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalles del juego: {str(e)}")
