from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..database import get_db
from .. import models, schemas
from ..utils.recommendation_engine import recommendation_engine
from ..utils.rawg_api import rawg_api  # Añadida importación faltante

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)

@router.get("/for-user/{user_id}", response_model=List[schemas.JuegoRecomendado])
def get_recommendations_for_user(
    user_id: int,
    max_price: Optional[float] = Query(None, description="Precio máximo para filtrar juegos (opcional)"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de recomendaciones"),
    db: Session = Depends(get_db)
):
    """
    Genera recomendaciones de juegos indies para un usuario específico.
    
    Este endpoint analiza los juegos favoritos del usuario para crear un perfil de preferencias
    basado en sus géneros preferidos y precio máximo. Luego busca juegos similares en la base de datos.
    
    El algoritmo de recomendación:
    1. Extrae todos los géneros de los juegos favoritos del usuario
    2. Calcula la frecuencia de cada género para determinar preferencias
    3. Asigna puntuaciones a juegos según la coincidencia con las preferencias
    4. Filtra por precio máximo que el usuario está dispuesto a pagar
    5. Ordena los resultados por relevancia (puntuación)
    
    Cada juego recomendado incluye una puntuación que indica qué tan relevante es para el usuario,
    donde valores más altos indican mayor relevancia.
    
    - **user_id**: ID del usuario para generar recomendaciones
    - **max_price**: Precio máximo (si no se especifica, usa el configurado en el perfil)
    - **limit**: Número de recomendaciones a devolver
    
    El sistema no recomienda juegos que el usuario ya tiene marcados como favoritos.
    
    Ejemplo de uso:
    ```
    GET /api/recommendations/for-user/1?max_price=25&limit=10
    ```
    """
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Check if the user has favorite games
    favorite_games = db.query(models.FavoriteGame).filter(models.FavoriteGame.user_id == user_id).all()
    if not favorite_games:
        raise HTTPException(status_code=400, detail="El usuario no tiene juegos favoritos.")
    
    # Generar recomendaciones
    recommendations = recommendation_engine.recommend_games(
        user_id=user_id,
        max_price=max_price,
        limit=limit,
        db=db
    )
    
    if not recommendations:
        return []
    
    return recommendations

@router.get("/by-genres", response_model=List[schemas.JuegoRecomendado])
def get_recommendations_by_genres(
    genres: List[str] = Query(..., description="Lista de géneros preferidos (ej: ['Action', 'Adventure', 'RPG'])"),
    max_price: float = Query(None, description="Precio máximo a pagar por juegos"),
    limit: int = Query(10, ge=1, le=50, description="Número máximo de recomendaciones"),
    db: Session = Depends(get_db)
):
    """
    Genera recomendaciones de juegos indies basadas en géneros específicos.
    
    Este endpoint permite obtener recomendaciones sin necesidad de tener un usuario registrado,
    especificando directamente los géneros de interés.
    
    Ejemplos de géneros populares:
    * Action (Acción)
    * Adventure (Aventura)
    * RPG
    * Strategy (Estrategia)
    * Simulation (Simulación)
    * Puzzle
    * Platformer (Plataformas)
    * Roguelike
    * Survival (Supervivencia)
    
    El algoritmo asigna pesos iguales a todos los géneros proporcionados y recomienda
    juegos que mejor coinciden con estas preferencias, ordenados por relevancia.
    
    - **genres**: Lista de géneros preferidos por el usuario
    - **max_price**: Filtro de precio máximo para los juegos
    - **limit**: Número de recomendaciones a devolver
    
    Las recomendaciones incluyen una puntuación de relevancia donde valores más 
    altos indican mayor coincidencia con los géneros especificados.
    
    Ejemplo de uso:
    ```
    GET /api/recommendations/by-genres?genres=Action&genres=RPG&max_price=20&limit=5
    ```
    """
    # Crear diccionario de preferencias de géneros con pesos iguales
    genre_preferences = {genre: 1.0/len(genres) for genre in genres}
    
    try:
        # Obtener juegos dentro del presupuesto
        query = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones)
        
        if max_price is not None and max_price > 0:
            query = query.filter(models.JuegosScrapeadoDeSteamParaRecomendaiones.precio <= max_price)
        
        potential_games = query.all()
        
        if not potential_games:
            return []
        
        # Calcular puntuación para cada juego
        scored_games = []
        for game in potential_games:
            score = recommendation_engine.calculate_game_score(game, genre_preferences)
            scored_games.append({
                "juego": game,
                "puntuacion": score
            })
        
        # Ordenar por puntuación descendente
        scored_games.sort(key=lambda x: x["puntuacion"], reverse=True)
        
        # Limitar y convertir a formato de salida
        recommendations = []
        for item in scored_games[:limit]:
            game = item["juego"]
            recommendations.append({
                "id": game.id,
                "nombre": game.nombre,
                "generos": game.generos,
                "precio": game.precio,
                "descripcion": game.descripcion,
                "imagen_principal": game.imagen_principal,
                "puntuacion": item["puntuacion"]
            })
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando recomendaciones: {str(e)}"
        )

@router.get("/games/{user_id}", response_model=List[Dict[str, Any]])
def get_game_recommendations(
    user_id: int,
    max_price: float = Query(None, description="Precio máximo (si es None, usa el del usuario)"),
    limit: int = Query(10, description="Número máximo de recomendaciones"),
    db: Session = Depends(get_db)
):
    """
    Genera recomendaciones de juegos para un usuario basado en sus preferencias
    
    Args:
        user_id: ID del usuario
        max_price: Precio máximo para filtrar juegos (opcional)
        limit: Número máximo de recomendaciones
        
    Returns:
        Lista de juegos recomendados con puntuación
    """
    try:
        # Verificar que el usuario existe
        user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Obtener recomendaciones usando el motor de recomendaciones
        recommendations = recommendation_engine.recommend_games(
            user_id=user_id,
            max_price=max_price,
            limit=limit,
            db=db
        )
        
        if not recommendations:
            return []
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando recomendaciones: {str(e)}")

@router.get("/similar-to/{game_id}", response_model=List[schemas.JuegoRecomendado])
def get_recommendations_similar_to_game(
    game_id: int,
    limit: int = Query(5, ge=1, le=20, description="Número máximo de recomendaciones"),
    db: Session = Depends(get_db)
):
    """
    Genera recomendaciones de juegos similares a un juego específico.
    """
    try:
        # Obtener información del juego
        game_info = rawg_api.get_game(game_id)
        if not game_info:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        
        # Extraer géneros
        genres = [genre["name"] for genre in game_info.get("genres", [])]
        
        if not genres:
            return []
        
        # Usar el endpoint existente de recomendaciones por géneros
        return get_recommendations_by_genres(genres=genres, limit=limit, db=db)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al obtener recomendaciones: {str(e)}")

@router.get("/trending", response_model=List[schemas.JuegoRecomendado])
def get_trending_recommendations(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de recomendaciones"),
    db: Session = Depends(get_db)
):
    """
    Obtiene juegos en tendencia como recomendaciones.
    """
    try:
        # Obtener juegos en tendencia desde RAWG
        trending_games = rawg_api.get_trending_games(1, limit)
        
        if not trending_games or "results" not in trending_games:
            return []
        
        # Convertir al formato de recomendaciones
        recommendations = []
        for game in trending_games.get("results", [])[:limit]:
            # Extraer géneros
            genres = [genre["name"] for genre in game.get("genres", [])]
            
            # Crear objeto de recomendación
            rec = {
                "id": game["id"],
                "nombre": game["name"],
                "generos": genres,
                "precio": round(15 + game.get("rating", 0) * 2, 2),  # Precio simulado
                "descripcion": game.get("description", ""),
                "imagen_principal": game.get("background_image", ""),
                "puntuacion": min(1.0, game.get("rating", 0) / 5)  # Convertir a escala 0-1
            }
            
            recommendations.append(rec)
        
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al obtener tendencias: {str(e)}")  # Corregido paréntesis
