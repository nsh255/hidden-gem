from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..utils.rawg_api import rawg_api  # Add this import

router = APIRouter(
    prefix="/favorite-games",
    tags=["favorite-games"],
)

@router.post("/", response_model=schemas.JuegoFavorito, status_code=status.HTTP_201_CREATED)
def create_favorite_game(game: schemas.JuegoFavoritoCreate, db: Session = Depends(get_db)):
    # Verificar si el juego ya existe
    db_game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter(
        models.JuegosFavoritosDeUsuarioQueProvienenDeRawg.nombre == game.nombre
    ).first()
    
    if db_game:
        return db_game
    
    # Crear nuevo juego
    db_game = models.JuegosFavoritosDeUsuarioQueProvienenDeRawg(**game.dict())
    
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

@router.get("/", response_model=List[schemas.JuegoFavorito])
def read_favorite_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).offset(skip).limit(limit).all()
    return games

@router.post("/add-favorite", status_code=status.HTTP_200_OK)
def add_favorite_to_user(favorite: schemas.FavoritoAdd, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == favorite.usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el juego existe en nuestra base de datos
    game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter(
        models.JuegosFavoritosDeUsuarioQueProvienenDeRawg.id == favorite.juego_id
    ).first()
    
    # Si el juego no existe en nuestra base, intentamos obtenerlo de RAWG y crearlo
    if not game:
        try:
            # Obtener datos del juego desde RAWG API
            game_data = rawg_api.get_game(favorite.juego_id)
            if not game_data:
                raise HTTPException(status_code=404, detail="Juego no encontrado en RAWG")
            
            # Extraer géneros y tags
            generos = [genre["name"] for genre in game_data.get("genres", [])]
            tags = [tag["name"] for tag in game_data.get("tags", [])] if "tags" in game_data else []
            
            # Crear el juego en nuestra base de datos
            game = models.JuegosFavoritosDeUsuarioQueProvienenDeRawg(
                id=favorite.juego_id,  # Usar el mismo ID que en RAWG
                nombre=game_data["name"],
                imagen=game_data.get("background_image", ""),
                descripcion=game_data.get("description", ""),
                generos=generos,
                tags=tags
            )
            
            db.add(game)
            db.commit()
            db.refresh(game)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear el juego: {str(e)}"
            )
    
    # Verificar si ya es favorito
    if game in user.juegos_favoritos:
        raise HTTPException(status_code=400, detail="El juego ya es favorito del usuario")
    
    # Añadir a favoritos
    user.juegos_favoritos.append(game)
    db.commit()
    
    return {"message": "Juego añadido a favoritos"}

@router.post("/add-steam-favorite", status_code=status.HTTP_200_OK)
def add_steam_favorite_to_user(favorite_data: dict, db: Session = Depends(get_db)):
    """
    Añade un juego de Steam a los favoritos del usuario.
    Este endpoint recibe los datos del juego directamente en lugar de buscarlos en RAWG.
    """
    usuario_id = favorite_data.get("usuario_id")
    juego_id = favorite_data.get("juego_id")
    game_data = favorite_data.get("game_data", {})
    
    # Verificar que los datos requeridos estén presentes
    if not usuario_id or not juego_id or not game_data:
        raise HTTPException(
            status_code=400, 
            detail="Datos incompletos para añadir juego de Steam a favoritos"
        )
    
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el juego existe en nuestra base de datos
    game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter(
        models.JuegosFavoritosDeUsuarioQueProvienenDeRawg.id == juego_id
    ).first()
    
    # Si el juego no existe en nuestra base, lo creamos con los datos proporcionados
    if not game:
        try:
            # Extraer datos del juego enviados desde el frontend
            generos = game_data.get("generos", [])
            tags = game_data.get("tags", [])
            
            # Crear el juego en nuestra base de datos
            game = models.JuegosFavoritosDeUsuarioQueProvienenDeRawg(
                id=juego_id,
                nombre=game_data.get("nombre", "Juego de Steam"),
                imagen=game_data.get("imagen", ""),
                descripcion=game_data.get("descripcion", ""),
                generos=generos,
                tags=tags
            )
            
            db.add(game)
            db.commit()
            db.refresh(game)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear el juego de Steam: {str(e)}"
            )
    
    # Verificar si ya es favorito
    if game in user.juegos_favoritos:
        raise HTTPException(status_code=400, detail="El juego ya es favorito del usuario")
    
    # Añadir a favoritos
    user.juegos_favoritos.append(game)
    db.commit()
    
    return {"message": "Juego de Steam añadido a favoritos"}

@router.delete("/remove-favorite", status_code=status.HTTP_200_OK)
def remove_favorite_from_user(favorite: schemas.FavoritoAdd, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == favorite.usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el juego existe
    game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter(
        models.JuegosFavoritosDeUsuarioQueProvienenDeRawg.id == favorite.juego_id
    ).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    # Verificar si es favorito
    if game not in user.juegos_favoritos:
        raise HTTPException(status_code=400, detail="El juego no es favorito del usuario")
    
    # Quitar de favoritos
    user.juegos_favoritos.remove(game)
    db.commit()
    
    return {"message": "Juego eliminado de favoritos"}

@router.get("/user/{user_id}", response_model=List[schemas.JuegoFavorito])
def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    favorites = user.juegos_favoritos
    if not favorites:
        return []  # Return an empty list if no favorites
    return favorites

@router.get("/check/{user_id}/{game_id}", response_model=bool)
def check_game_is_favorite(user_id: int, game_id: int, db: Session = Depends(get_db)):
    """
    Verifica si un juego específico está entre los favoritos de un usuario.
    
    Args:
        user_id: ID del usuario
        game_id: ID del juego a verificar
        
    Returns:
        True si el juego está en favoritos, False en caso contrario
    """
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el juego existe en la base de datos
    game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter(
        models.JuegosFavoritosDeUsuarioQueProvienenDeRawg.id == game_id
    ).first()
    
    if not game:
        # Si el juego no existe en la base de datos, definitivamente no es favorito
        return False
    
    # Verificar si el juego está en la lista de favoritos del usuario
    is_favorite = game in user.juegos_favoritos
    
    return is_favorite
