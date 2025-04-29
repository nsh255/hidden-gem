from typing import List, Dict, Set
from sqlalchemy.orm import Session
from app.models.game import Game
from app.models.user import User
import logging
from collections import Counter

# Configurar logging
logger = logging.getLogger(__name__)

def get_game_recommendations(user_id: int, db: Session, limit: int = 10) -> List[Game]:
    """
    Recomienda juegos basados en los favoritos de un usuario.
    
    Args:
        user_id (int): ID del usuario
        db (Session): Sesión de base de datos
        limit (int): Número máximo de recomendaciones (default: 10)
        
    Returns:
        List[Game]: Lista de juegos recomendados
    """
    # Obtener usuario y sus restricciones
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Usuario con ID {user_id} no encontrado")
        return []
    
    # Verificar si el usuario tiene juegos favoritos
    if not user.favorite_games:
        logger.info(f"Usuario {user_id} no tiene juegos favoritos para generar recomendaciones")
        return []
    
    # Extraer tags y géneros de los juegos favoritos
    favorite_tags = _extract_tags(user.favorite_games)
    favorite_genres = _extract_genres(user.favorite_games)
    
    # Obtener IDs de juegos ya favoritos para excluirlos
    favorite_ids = {game.id for game in user.favorite_games}
    
    # Buscar juegos indie que no estén en favoritos y cumplan con el precio máximo
    candidate_games = (
        db.query(Game)
        .filter(Game.id.notin_(favorite_ids))
        .filter(Game.is_indie == True)
        .filter(Game.price <= user.max_price)
        .all()
    )
    
    # Calcular puntuación para cada juego candidato
    scored_games = []
    for game in candidate_games:
        score = _calculate_similarity_score(
            game, 
            favorite_tags, 
            favorite_genres
        )
        scored_games.append((game, score))
    
    # Ordenar juegos por puntuación descendente
    scored_games.sort(key=lambda x: x[1], reverse=True)
    
    # Devolver los N juegos con mayor puntuación
    recommendations = [game for game, score in scored_games[:limit]]
    
    return recommendations

def _extract_tags(games: List[Game]) -> Dict[str, int]:
    """
    Extrae y cuenta las frecuencias de tags de una lista de juegos.
    
    Args:
        games (List[Game]): Lista de juegos
        
    Returns:
        Dict[str, int]: Diccionario de tags y sus frecuencias
    """
    tag_counter = Counter()
    
    for game in games:
        if game.tags:
            # Las tags están almacenadas como string separado por comas
            game_tags = [tag.strip() for tag in game.tags.split(',')]
            tag_counter.update(game_tags)
    
    return tag_counter

def _extract_genres(games: List[Game]) -> Dict[str, int]:
    """
    Extrae y cuenta las frecuencias de géneros de una lista de juegos.
    
    Args:
        games (List[Game]): Lista de juegos
        
    Returns:
        Dict[str, int]: Diccionario de géneros y sus frecuencias
    """
    genre_counter = Counter()
    
    for game in games:
        if game.genres:
            # Los géneros están almacenados como string separado por comas
            game_genres = [genre.strip() for genre in game.genres.split(',')]
            genre_counter.update(game_genres)
    
    return genre_counter

def _calculate_similarity_score(game: Game, favorite_tags: Dict[str, int], favorite_genres: Dict[str, int]) -> float:
    """
    Calcula la puntuación de similitud de un juego con respecto a los favoritos.
    
    Args:
        game (Game): Juego a comparar
        favorite_tags (Dict[str, int]): Contador de tags favoritas
        favorite_genres (Dict[str, int]): Contador de géneros favoritos
        
    Returns:
        float: Puntuación de similitud
    """
    score = 0.0
    
    # Procesar tags del juego
    if game.tags:
        game_tags = [tag.strip() for tag in game.tags.split(',')]
        for tag in game_tags:
            # Sumar la frecuencia de cada tag coincidente
            score += favorite_tags.get(tag, 0) * 1.0
    
    # Procesar géneros del juego (los géneros tienen más peso)
    if game.genres:
        game_genres = [genre.strip() for genre in game.genres.split(',')]
        for genre in game_genres:
            # Sumar la frecuencia de cada género coincidente (con más peso)
            score += favorite_genres.get(genre, 0) * 2.5
    
    # Normalizar la puntuación por el número de tags y géneros
    # para no favorecer juegos con muchos tags/géneros
    total_elements = len(game.tags.split(',') if game.tags else []) + len(game.genres.split(',') if game.genres else [])
    if total_elements > 0:
        score = score / total_elements
    
    return score

def get_recommendations_by_game(game_id: int, user_id: int, db: Session, limit: int = 10) -> List[Game]:
    """
    Recomienda juegos similares a un juego específico, respetando el precio máximo del usuario.
    
    Args:
        game_id (int): ID del juego base
        user_id (int): ID del usuario para considerar su precio máximo
        db (Session): Sesión de base de datos
        limit (int): Número máximo de recomendaciones
        
    Returns:
        List[Game]: Lista de juegos recomendados
    """
    # Obtener el juego base
    base_game = db.query(Game).filter(Game.id == game_id).first()
    if not base_game:
        return []
    
    # Obtener usuario para verificar precio máximo
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    # Extraer tags y géneros del juego base
    base_tags = Counter({tag.strip(): 1 for tag in base_game.tags.split(',')}) if base_game.tags else Counter()
    base_genres = Counter({genre.strip(): 1 for genre in base_game.genres.split(',')}) if base_game.genres else Counter()
    
    # Buscar juegos indie que no sean el juego base y cumplan con el precio máximo
    candidate_games = (
        db.query(Game)
        .filter(Game.id != game_id)
        .filter(Game.is_indie == True)
        .filter(Game.price <= user.max_price)
        .all()
    )
    
    # Calcular puntuación para cada juego candidato
    scored_games = []
    for game in candidate_games:
        score = _calculate_similarity_score(game, base_tags, base_genres)
        scored_games.append((game, score))
    
    # Ordenar juegos por puntuación descendente
    scored_games.sort(key=lambda x: x[1], reverse=True)
    
    # Devolver los N juegos con mayor puntuación
    recommendations = [game for game, score in scored_games[:limit]]
    
    return recommendations
