from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas
from ..utils.recommendation_engine import recommendation_engine

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
    """
    # Verificar si el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
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
