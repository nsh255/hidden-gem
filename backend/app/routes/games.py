from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..database import get_db
from .. import models, schemas
from ..utils.rawg_api import rawg_api
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from ..config import settings
import random

router = APIRouter(
    prefix="/games",
    tags=["games"],
)

# Configuración JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Lista común de palabras clave sexuales
sexual_keywords = [
    "sexual", "nudity", "adult", "erotic", "porn", "hentai", "ecchi", 
    "fetish", "provocative", "explicit", "mature", "xxx", "nsfw", "ntr", 
    "sensual", "seductive", "intimate", "suggestive", "lewd", "obscene",
    # Términos adicionales
    "girlfriend", "boyfriend", "dating", "romance", "sexy", "hot",
    "love", "kiss", "touching", "strip", "undress", "lingerie", "bra",
    "underwear", "bikini", "swimsuit", "pleasure", "desire", "passion",
    "flirt", "seduce", "lust", "fantasy", "waifu", "huniepop", "dream daddy",
    "hatoful", "boob", "breast", "butt", "ass", "grope", "panty", "thong",
    "dating sim", "visual novel", "relationship", "body", "naked", "shower",
    "bath", "beach", "model", "pose", "tease", "tempt", "virgin", "virgin*",
    "hookup", "affair", "50 shades", "topless", "onlyfans", "dress up"
]

# Nueva función para verificar si un juego tiene contenido sexual
def has_sexual_content(game):
    """Comprueba si un juego contiene palabras clave sexuales en su título o descripción"""
    # Verificar explícitamente el título (prioridad alta)
    if game.get("name"):
        game_name = game.get("name", "").lower()
        if any(keyword in game_name for keyword in sexual_keywords):
            return True
    
    # Verificar la descripción completa
    if game.get("description"):
        game_desc = game.get("description", "").lower()
        if any(keyword in game_desc for keyword in sexual_keywords):
            return True
    
    # Verificar la combinación de título y descripción
    combined_text = (game.get("name", "").lower() + " " + game.get("description", "").lower())
    if any(keyword in combined_text for keyword in sexual_keywords):
        return True
    
    return False

@router.get("/", response_model=Dict[str, Any])
def get_games(
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(12, description="Elementos por página"),
    genre: Optional[int] = Query(None, description="ID del género para filtrar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista paginada de juegos.
    
    Si se proporciona un ID de género, filtra los juegos por ese género.
    """
    try:
        # Para este endpoint, utilizaremos la API de RAWG para obtener juegos
        # ya que probablemente tiene más datos que nuestra base de datos local
        
        # Si hay un género especificado, usamos un endpoint diferente
        if genre:
            result = rawg_api.get_games_by_genre(genre, page, page_size)
        else:
            result = rawg_api.get_games(page, page_size)
        
        # Ensure RAWG API response is valid
        if not result or "results" not in result:
            # Provide a fallback response structure to prevent frontend errors
            return {
                "count": 0,
                "next": None,
                "previous": None,
                "results": []
            }
        
        # Añadimos precios simulados a los juegos
        for game in result.get("results", []):
            # Precio simulado basado en rating (mejor rating = precio más alto)
            if "rating" in game:
                base_price = 14.99
                rating_factor = game.get("rating", 0) / 5.0  # Normalizar a 0-1
                game["price"] = round(base_price + (10 * rating_factor), 2)
            else:
                game["price"] = 14.99
        
        # Filtrar juegos con contenido sexual usando la nueva función
        result["results"] = [
            game for game in result.get("results", [])
            if not has_sexual_content(game)
        ]
        
        return result
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error getting games: {str(e)}")
        # Return a valid empty response instead of raising an exception
        return {
            "count": 0,
            "next": None,
            "previous": None,
            "results": []
        }

@router.get("/filter", response_model=Dict[str, Any])
def filter_games(
    min_price: Optional[float] = Query(None, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, description="Precio máximo"),
    genres: List[int] = Query(None, description="IDs de géneros"),
    platforms: List[int] = Query(None, description="IDs de plataformas"),
    sort_by: Optional[str] = Query(None, description="Campo por el que ordenar"),
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(12, description="Elementos por página"),
    db: Session = Depends(get_db)
):
    """
    Filtra juegos por diversos criterios como precio, géneros, plataformas, etc.
    """
    try:
        # Para mantener la consistencia con otros endpoints, utilizamos la API de RAWG
        # y aplicamos los filtros disponibles
        
        # Construir la lista de parámetros para la API
        params = {
            "page": page,
            "page_size": page_size
        }
        
        # Añadir filtros que soporta la API de RAWG
        if genres:
            # La API de RAWG espera una cadena separada por comas
            params["genres"] = ",".join(str(g) for g in genres)
        
        if platforms:
            params["platforms"] = ",".join(str(p) for p in platforms)
        
        if sort_by:
            params["ordering"] = sort_by
        
        # Obtener juegos con los filtros aplicados
        result = rawg_api.get_games_with_filters(params)
        
        if not result:
            raise HTTPException(status_code=503, detail="Error al conectar con RAWG API")
        
        # Añadir precios simulados y filtrar por precio y contenido sexual
        filtered_results = []
        for game in result.get("results", []):
            # Precio simulado
            if "rating" in game:
                base_price = 14.99
                rating_factor = game.get("rating", 0) / 5.0
                price = round(base_price + (10 * rating_factor), 2)
            else:
                price = 14.99
            
            game["price"] = price
            
            # Solo añadir juegos sin contenido sexual y que cumplan el filtro de precio
            if not has_sexual_content(game) and (min_price is None or price >= min_price) and (max_price is None or price <= max_price):
                filtered_results.append(game)
        
        # Actualizar el recuento y los resultados
        result["results"] = filtered_results
        result["count"] = len(filtered_results)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al filtrar juegos: {str(e)}")

@router.get("/{game_id}/similar", response_model=List[Dict[str, Any]])
def get_similar_games(
    game_id: int,
    page: int = Query(1, description="Página de resultados"),
    limit: int = Query(4, description="Número máximo de juegos similares por página"),
    db: Session = Depends(get_db)
):
    """
    Obtiene juegos similares a un juego específico.
    Soporta paginación para ver más juegos similares.
    """
    try:
        # Obtener detalles del juego
        game_details = rawg_api.get_game(game_id)
        if not game_details:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Obtener géneros del juego
        genres = [genre["slug"] for genre in game_details.get("genres", [])]
        
        if not genres:
            return []
        
        # Obtener juegos similares basados en géneros con paginación
        # Multiplicamos por page para simular paginación en la API
        total_to_fetch = limit * page + 1  # Obtenemos uno extra para asegurar contenido suficiente
        similar_games = rawg_api.get_games_by_genres(genres, 1, total_to_fetch)
        
        if not similar_games or "results" not in similar_games:
            return []
        
        # Filtrar el juego actual de los resultados y añadir precios simulados
        all_results = []
        for game in similar_games.get("results", []):
            if game["id"] != game_id:
                # Añadir precio simulado
                if "rating" in game:
                    base_price = 14.99
                    rating_factor = game.get("rating", 0) / 5.0
                    game["price"] = round(base_price + (10 * rating_factor), 2)
                else:
                    game["price"] = 14.99
                
                all_results.append(game)
        
        # Filtrar juegos con contenido sexual
        all_results = [
            game for game in all_results
            if not has_sexual_content(game)
        ]
        
        # Aplicar paginación
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paged_results = all_results[start_idx:end_idx]
        
        # Añadir flag para indicar si hay más resultados
        has_more = end_idx < len(all_results)
        for game in paged_results:
            game["has_more"] = has_more
        
        return paged_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener juegos similares: {str(e)}")

@router.get("/{game_id}/reviews", response_model=Dict[str, Any])
def get_game_reviews(
    game_id: int,
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(10, description="Elementos por página"),
    db: Session = Depends(get_db)
):
    """
    Obtiene las reseñas de un juego específico.
    """
    try:
        # Verificar si el juego existe
        game = rawg_api.get_game(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Como no tenemos reseñas reales en la base de datos, generamos algunas de ejemplo
        # En una implementación real, buscaríamos reseñas en la base de datos
        
        # Reseñas de ejemplo
        sample_reviews = [
            {
                "id": 1,
                "user_id": 1,
                "user_name": "Usuario1",
                "game_id": game_id,
                "rating": 4.5,
                "content": "Excelente juego con una historia cautivadora y gráficos impresionantes.",
                "created_at": "2023-01-15T14:30:00"
            },
            {
                "id": 2,
                "user_id": 2,
                "user_name": "Usuario2",
                "game_id": game_id,
                "rating": 3.8,
                "content": "Buen juego pero con algunos problemas de rendimiento en ciertas secciones.",
                "created_at": "2023-02-20T09:15:00"
            },
            {
                "id": 3,
                "user_id": 3,
                "user_name": "Usuario3",
                "game_id": game_id,
                "rating": 5.0,
                "content": "¡Obra maestra! Una de las mejores experiencias que he tenido en videojuegos.",
                "created_at": "2023-03-05T18:45:00"
            }
        ]
        
        # Simular paginación
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return {
            "count": len(sample_reviews),
            "results": sample_reviews[start_idx:end_idx]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reseñas: {str(e)}")

@router.post("/{game_id}/reviews", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def add_game_review(
    game_id: int,
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db)
):
    """
    Añade una reseña para un juego específico.
    """
    try:
        # Verificar si el juego existe
        game = rawg_api.get_game(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # En una implementación real, guardaríamos la reseña en la base de datos
        # Aquí simplemente devolvemos una respuesta simulada
        
        return {
            "id": 999,  # ID simulado
            "user_id": 1,  # ID de usuario simulado (normalmente sería el usuario autenticado)
            "user_name": "UsuarioActual",
            "game_id": game_id,
            "rating": review.rating,
            "content": review.content,
            "created_at": "2023-05-10T12:00:00"  # Fecha simulada
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al añadir reseña: {str(e)}")

@router.get("/genres", response_model=List[Dict[str, Any]])
def get_genres(db: Session = Depends(get_db)):
    """
    Obtiene la lista de géneros de juegos disponibles.
    """
    try:
        # Obtener géneros desde RAWG
        genres = rawg_api.get_genres()
        
        if not genres or "results" not in genres:
            return []
        
        # Retornar solo los datos necesarios (id y nombre)
        return [{"id": genre["id"], "name": genre["name"]} for genre in genres.get("results", [])]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener géneros: {str(e)}")
