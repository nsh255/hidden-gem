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
    favorite_publishers = _extract_publishers(user.favorite_games)
    
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
            favorite_genres,
            favorite_publishers
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
            # Manejo flexible del formato de tags (lista o string)
            if isinstance(game.tags, list):
                game_tags = [tag.strip() for tag in game.tags]
            else:
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
            # Manejo flexible del formato de géneros (lista o string)
            if isinstance(game.genres, list):
                game_genres = [genre.strip() for genre in game.genres]
            else:
                game_genres = [genre.strip() for genre in game.genres.split(',')]
            genre_counter.update(game_genres)
    
    return genre_counter

def _extract_publishers(games: List[Game]) -> Dict[str, int]:
    """
    Extrae y cuenta las frecuencias de publishers de una lista de juegos.
    
    Args:
        games (List[Game]): Lista de juegos
        
    Returns:
        Dict[str, int]: Diccionario de publishers y sus frecuencias
    """
    publisher_counter = Counter()
    
    for game in games:
        if game.publishers:
            # Manejo flexible del formato de publishers (lista o string)
            if isinstance(game.publishers, list):
                game_publishers = [publisher.strip() for publisher in game.publishers]
            else:
                game_publishers = [publisher.strip() for publisher in game.publishers.split(',')]
            publisher_counter.update(game_publishers)
    
    return publisher_counter

def _calculate_similarity_score(game: Game, favorite_tags: Dict[str, int], 
                              favorite_genres: Dict[str, int], 
                              favorite_publishers: Dict[str, int]) -> float:
    """
    Calcula la puntuación de similitud de un juego con respecto a los favoritos.
    
    Args:
        game (Game): Juego a comparar
        favorite_tags (Dict[str, int]): Contador de tags favoritas
        favorite_genres (Dict[str, int]): Contador de géneros favoritos
        favorite_publishers (Dict[str, int]): Contador de publishers favoritos
        
    Returns:
        float: Puntuación de similitud
    """
    score = 0.0
    
    # Procesar tags del juego con manejo flexible de formato
    if game.tags:
        if isinstance(game.tags, list):
            game_tags = [tag.strip() for tag in game.tags]
        else:
            game_tags = [tag.strip() for tag in game.tags.split(',')]
            
        for tag in game_tags:
            # Sumar la frecuencia de cada tag coincidente
            score += favorite_tags.get(tag, 0) * 1.0
    
    # Procesar géneros del juego (los géneros tienen más peso)
    if game.genres:
        if isinstance(game.genres, list):
            game_genres = [genre.strip() for genre in game.genres]
        else:
            game_genres = [genre.strip() for genre in game.genres.split(',')]
            
        for genre in game_genres:
            # Sumar la frecuencia de cada género coincidente (con más peso)
            score += favorite_genres.get(genre, 0) * 2.5
    
    # Procesar publishers del juego (con peso intermedio)
    if game.publishers:
        if isinstance(game.publishers, list):
            game_publishers = [publisher.strip() for publisher in game.publishers]
        else:
            game_publishers = [publisher.strip() for publisher in game.publishers.split(',')]
            
        for publisher in game_publishers:
            # Sumar la frecuencia de cada publisher coincidente (con peso intermedio)
            score += favorite_publishers.get(publisher, 0) * 1.5
    
    # Normalizar la puntuación por el número de tags, géneros y publishers
    total_elements = 0
    if game.tags:
        total_elements += len(game.tags if isinstance(game.tags, list) else game.tags.split(','))
    if game.genres:
        total_elements += len(game.genres if isinstance(game.genres, list) else game.genres.split(','))
    if game.publishers:
        total_elements += len(game.publishers if isinstance(game.publishers, list) else game.publishers.split(','))
    
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
    
    # Extraer tags y géneros del juego base con manejo flexible de formato
    if base_game.tags:
        if isinstance(base_game.tags, list):
            base_tags = Counter({tag.strip(): 1 for tag in base_game.tags})
        else:
            base_tags = Counter({tag.strip(): 1 for tag in base_game.tags.split(',')})
    else:
        base_tags = Counter()
        
    if base_game.genres:
        if isinstance(base_game.genres, list):
            base_genres = Counter({genre.strip(): 1 for genre in base_game.genres})
        else:
            base_genres = Counter({genre.strip(): 1 for genre in base_game.genres.split(',')})
    else:
        base_genres = Counter()
    
    if base_game.publishers:
        if isinstance(base_game.publishers, list):
            base_publishers = Counter({publisher.strip(): 1 for publisher in base_game.publishers})
        else:
            base_publishers = Counter({publisher.strip(): 1 for publisher in base_game.publishers.split(',')})
    else:
        base_publishers = Counter()
    
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
        score = _calculate_similarity_score(game, base_tags, base_genres, base_publishers)
        scored_games.append((game, score))
    
    # Ordenar juegos por puntuación descendente
    scored_games.sort(key=lambda x: x[1], reverse=True)
    
    # Devolver los N juegos con mayor puntuación
    recommendations = [game for game, score in scored_games[:limit]]
    
    return recommendations
