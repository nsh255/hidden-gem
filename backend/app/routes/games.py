from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import JWTError, jwt
from app.database import get_db
from app.models.game import Game
from app.models.user import User
from app.schemas.game import GameOut
from app.routes.auth import oauth2_scheme
from app.core.security import SECRET_KEY, ALGORITHM

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Función para obtener el usuario autenticado actual a partir del token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user

@router.get("/", response_model=List[GameOut])
async def get_games(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene juegos filtrados según el precio máximo del usuario autenticado
    """
    # Filtra juegos que no excedan el precio máximo del usuario
    games = db.query(Game).filter(Game.price <= current_user.max_price).offset(skip).limit(limit).all()
    return games

@router.get("/{game_id}", response_model=GameOut)
async def get_game(
    game_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles de un juego específico por su ID
    """
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró juego con id: {game_id}"
        )
    return game

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
