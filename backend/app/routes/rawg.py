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
    Obtiene detalles completos de un juego específico desde RAWG
    """
    try:
        game = get_game_details(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return game
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalles del juego: {str(e)}")
