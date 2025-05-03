from fastapi import APIRouter, Depends, HTTPException, Query, status
import requests
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas
from ..utils.rawg_api import rawg_api

router = APIRouter(
    prefix="/rawg",
    tags=["rawg-games"],
)

@router.get("/search", response_model=dict)
def search_rawg_games(
    query: str = Query(..., description="Texto para buscar juegos"),
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(20, description="Elementos por página")
):
    """
    Busca juegos en la API de RAWG por nombre
    """
    result = rawg_api.search_games(query, page, page_size)
    if not result:
        raise HTTPException(status_code=503, detail="Error al conectar con RAWG API")
    return result

@router.get("/game/{game_id}", response_model=dict)
def get_rawg_game(game_id: int):
    """
    Obtiene los detalles de un juego específico de RAWG por su ID
    """
    result = rawg_api.get_game(game_id)
    if not result:
        raise HTTPException(status_code=404, detail="Juego no encontrado o error en la API")
    return result

@router.post("/add-to-favorites", status_code=status.HTTP_201_CREATED, response_model=schemas.JuegoFavorito)
def add_rawg_game_to_favorites(
    user_id: int, 
    game_id: int,
    db: Session = Depends(get_db)
):
    """
    Añade un juego de RAWG a los favoritos del usuario, 
    creando primero el registro del juego si no existe
    """
    # Verificar que el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener datos del juego desde RAWG
    game_data = rawg_api.get_game(game_id)
    if not game_data:
        raise HTTPException(status_code=404, detail="Juego no encontrado en RAWG")
    
    # Verificar si el juego ya existe en la base de datos
    db_game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter(
        models.JuegosFavoritosDeUsuarioQueProvienenDeRawg.nombre == game_data["name"]
    ).first()
    
    # Si no existe, crear el juego en la base de datos
    if not db_game:
        # Extraer géneros y tags
        generos = [genre["name"] for genre in game_data.get("genres", [])]
        tags = [tag["name"] for tag in game_data.get("tags", [])]
        
        # Crear objeto de juego
        db_game = models.JuegosFavoritosDeUsuarioQueProvienenDeRawg(
            nombre=game_data["name"],
            imagen=game_data.get("background_image", ""),
            descripcion=game_data.get("description", ""),
            generos=generos,
            tags=tags
        )
        
        db.add(db_game)
        db.commit()
        db.refresh(db_game)
    
    # Verificar si el juego ya es favorito del usuario
    if db_game in user.juegos_favoritos:
        raise HTTPException(
            status_code=400, 
            detail="Este juego ya está en la lista de favoritos del usuario"
        )
    
    # Añadir a favoritos
    user.juegos_favoritos.append(db_game)
    db.commit()
    
    return db_game

@router.get("/trending", response_model=dict)
def get_trending_games(
    page: int = Query(1, description="Número de página inicial"),
    page_size: int = Query(20, description="Elementos por página (máx. 40 recomendado)"),
    max_pages: int = Query(1, description="Número de páginas a recuperar (aumenta la cantidad de juegos)", ge=1, le=5)
):
    """
    Obtiene juegos populares o tendencia desde RAWG.
    
    Esta función permite recuperar más juegos en tendencia combinando resultados de múltiples páginas.
    
    - **page**: Página inicial para la búsqueda
    - **page_size**: Número de juegos por página (máximo recomendado: 40)
    - **max_pages**: Número de páginas a recuperar (1-5)
    
    Ejemplo: Para obtener 100 juegos en tendencia, puedes usar page_size=20 y max_pages=5
    """
    result = rawg_api.get_trending_games(page, page_size, max_pages)
    if not result:
        raise HTTPException(status_code=503, detail="Error al conectar con RAWG API")
    return result

@router.get("/random", response_model=dict)
def get_random_games(
    count: int = Query(10, description="Número de juegos aleatorios a recuperar", ge=1, le=50)
):
    """
    Obtiene una selección aleatoria de juegos desde RAWG.
    
    Esta función es útil para descubrir nuevos juegos de forma aleatoria o para
    presentar recomendaciones variadas a los usuarios.
    
    - **count**: Número de juegos aleatorios a devolver (entre 1 y 50)
    
    La función consulta diferentes páginas aleatorias de la API de RAWG para garantizar
    una mayor variedad en los resultados.
    """
    result = rawg_api.get_random_games(count)
    if not result:
        raise HTTPException(status_code=503, detail="Error al conectar con RAWG API")
    return result
