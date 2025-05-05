from fastapi import APIRouter, Depends, HTTPException, Query, status, Security
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..database import get_db
from .. import models, schemas
from ..utils.recommendation_engine import recommendation_engine
from ..utils.rawg_api import rawg_api
from ..config import settings  # Asumiendo que tienes esta configuración para JWT
import random

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)

# Reusamos el mismo esquema de seguridad OAuth2 de otros endpoints
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

# Función para obtener el usuario actual desde el token
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Extrae el ID del usuario del token JWT actual"""
    if not token:
        raise HTTPException(status_code=401, detail="No se proporcionó token de autenticación")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

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
    _t: Optional[str] = Query(None, description="Timestamp parameter to prevent caching"),
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
    - **_t**: Parámetro de timestamp para evitar cache
    
    Las recomendaciones incluyen una puntuación de relevancia donde valores más 
    altos indican mayor coincidencia con los géneros especificados.
    
    Ejemplo de uso:
    ```
    GET /api/recommendations/by-genres?genres=Action&genres=RPG&max_price=20&limit=5
    ```
    """
    # Crear diccionario de preferencias de géneros con pesos iguales
    genre_preferences = {genre: 1.0/len(genres) for genre in genres}
    
    import random  # Add import for randomization
    
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
            # Add randomization factor to ensure different results on each request
            random_factor = random.uniform(0.85, 1.15)
            scored_games.append({
                "juego": game,
                "puntuacion": score * random_factor
            })
        
        # Ordenar por puntuación descendente
        scored_games.sort(key=lambda x: x["puntuacion"], reverse=True)
        
        # Get more games than needed for randomization
        top_games = scored_games[:min(limit * 3, len(scored_games))]
        
        # Randomly select 'limit' games from the top games
        if len(top_games) > limit:
            selected_items = random.sample(top_games, limit)
        else:
            selected_items = top_games
        
        # Limitar y convertir a formato de salida
        recommendations = []
        for item in selected_items:
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

@router.get("/personalized", response_model=List[schemas.JuegoRecomendado])
def get_personalized_recommendations(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=50, description="Elementos por página"),
    max_price: Optional[float] = Query(None, description="Precio máximo (opcional)"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Genera recomendaciones personalizadas para el usuario autenticado.
    
    Este endpoint analiza los juegos favoritos del usuario actual para crear un perfil de preferencias
    y recomendar juegos similares. Soporta paginación para cargar más recomendaciones mientras se desplaza.
    
    - **page**: Número de página (comienza en 1)
    - **limit**: Número de elementos por página
    - **max_price**: Precio máximo opcional para filtrar juegos
    """
    # Verificar que el token esté presente
    if not token:
        raise HTTPException(status_code=401, detail="Se requiere autenticación para acceder a recomendaciones personalizadas")
    
    try:
        # Decodificar el token para obtener el ID del usuario
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido: no contiene ID de usuario")

        # Verificar si el usuario existe
        user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar si el usuario tiene juegos favoritos
        if not user.juegos_favoritos or len(user.juegos_favoritos) == 0:
            # Return consistent error code (400) and clear message
            return JSONResponse(
                status_code=400,
                content={"detail": "No tienes juegos favoritos para generar recomendaciones."}
            )
        
        # Calcular offset para paginación
        offset = (page - 1) * limit
        
        # Extraer géneros de todos los juegos favoritos
        all_genres = []
        for fav_game in user.juegos_favoritos:
            if hasattr(fav_game, 'generos') and fav_game.generos:
                all_genres.extend(fav_game.generos)
        
        # Si no hay géneros, devolvemos una lista vacía en lugar de error
        if not all_genres:
            return []
        
        # Tomar los géneros más comunes
        from collections import Counter
        common_genres = [genre for genre, _ in Counter(all_genres).most_common(5)]
        
        # Usar la función existente para obtener recomendaciones basadas en géneros
        timestamp = random.randint(1000000, 9999999)  # Timestamp aleatorio para evitar caché
        recommendations = get_recommendations_by_genres(
            genres=common_genres,
            max_price=max_price or user.precio_max,
            limit=limit * 3,  # Pedimos más para tener suficiente variedad
            _t=str(timestamp),
            db=db
        )
        
        # Aplicar paginación manual
        if offset >= len(recommendations):
            # Si el offset es mayor que el número de recomendaciones, devolvemos una lista vacía
            return []
        
        # Mezclar las recomendaciones para garantizar variedad en cada página
        if page > 1:
            random.shuffle(recommendations)
        
        # Obtener el segmento para la página actual
        paginated_recommendations = recommendations[offset:offset + limit]
        
        return paginated_recommendations
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token de autenticación inválido o expirado")
    except Exception as e:
        # Registrar el error para depuración
        import traceback
        print(f"Error en recomendaciones personalizadas: {str(e)}")
        print(traceback.format_exc())
        
        # Return consistent error code and message for debugging
        if "No tienes juegos favoritos" in str(e):
            return JSONResponse(
                status_code=400,
                content={"detail": "No tienes juegos favoritos para generar recomendaciones."}
            )
        
        # Devolver un error de manera controlada
        raise HTTPException(
            status_code=500, 
            detail="Error al generar recomendaciones. Por favor, inténtalo más tarde."
        )
