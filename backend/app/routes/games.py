from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
from app.database import get_db
from app.models.game import Game
from app.models.user import User
from app.schemas.game import GameOut, GameSearch
from app.routes.auth import oauth2_scheme, get_current_user
from app.core.security import SECRET_KEY, ALGORITHM
from sqlalchemy import or_, func

router = APIRouter()

@router.get("/", response_model=List[GameOut])
async def get_games(
    skip: int = 0, 
    limit: int = 100,
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    genres: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene juegos con filtros avanzados
    """
    query = db.query(Game)
    
    # Aplicar filtros si se proporcionan
    if name:
        query = query.filter(Game.name.ilike(f"%{name}%"))
    
    if min_price is not None:
        query = query.filter(Game.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Game.price <= max_price)
    
    if genres:
        # Filtrar por alguno de los géneros especificados
        query = query.filter(Game.genres.overlap(genres))
    
    if tags:
        # Filtrar por alguna de las etiquetas especificadas
        query = query.filter(Game.tags.overlap(tags))
    
    # Aplicar límites y paginación
    total = query.count()
    games = query.offset(skip).limit(limit).all()
    
    # Devolver el resultado con metadatos
    return games

@router.get("/{game_id}", response_model=GameOut)
async def get_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un juego específico por su ID
    """
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return game

@router.post("/search", response_model=List[GameOut])
async def search_games(
    search: GameSearch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Búsqueda avanzada de juegos con múltiples criterios
    """
    query = db.query(Game)
    
    # Búsqueda por texto en nombre o descripción
    if search.text:
        query = query.filter(
            or_(
                Game.name.ilike(f"%{search.text}%"),
                Game.description.ilike(f"%{search.text}%")
            )
        )
    
    # Filtros de precio
    if search.min_price is not None:
        query = query.filter(Game.price >= search.min_price)
    
    if search.max_price is not None:
        query = query.filter(Game.price <= search.max_price)
    
    # Filtros de géneros
    if search.genres:
        query = query.filter(Game.genres.overlap(search.genres))
    
    # Filtros de etiquetas
    if search.tags:
        query = query.filter(Game.tags.overlap(search.tags))
    
    # Ordenamiento
    if search.sort_by == "price_asc":
        query = query.order_by(Game.price.asc())
    elif search.sort_by == "price_desc":
        query = query.order_by(Game.price.desc())
    elif search.sort_by == "name":
        query = query.order_by(Game.name.asc())
    elif search.sort_by == "rating":
        query = query.order_by(Game.rating.desc())
    
    # Límite y paginación
    games = query.offset(search.skip).limit(search.limit).all()
    
    return games

@router.post("/favorite/{game_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Añade un juego a los favoritos del usuario autenticado
    """
    # Verificar si el juego existe
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró juego con id: {game_id}"
        )
    
    # Verificar si el juego ya está en favoritos
    if game in current_user.favorite_games:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este juego ya está en tus favoritos"
        )
    
    # Añadir juego a favoritos
    current_user.favorite_games.append(game)
    db.commit()
    
    return {"message": "Juego añadido a favoritos correctamente"}

@router.delete("/favorite/{game_id}", status_code=status.HTTP_200_OK)
async def remove_favorite_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un juego de los favoritos del usuario autenticado
    """
    # Verificar si el juego existe
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró juego con id: {game_id}"
        )
    
    # Verificar si el juego está en favoritos
    if game not in current_user.favorite_games:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este juego no está en tus favoritos"
        )
    
    # Eliminar juego de favoritos
    current_user.favorite_games.remove(game)
    db.commit()
    
    return {"message": "Juego eliminado de favoritos correctamente"}

@router.get("/user/favorites", response_model=List[GameOut])
async def get_favorite_games(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los juegos favoritos del usuario autenticado
    """
    return current_user.favorite_games

from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends, Query

class GameBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    url: Optional[str] = None
    app_id: Optional[str] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    developers: Optional[List[str]] = None  # Add developers field
    is_indie: bool = True
    source: str = "steam"

    class Config:
        orm_mode = True
