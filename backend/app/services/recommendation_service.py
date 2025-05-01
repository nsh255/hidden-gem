from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.game import Game
from app.models.user import User
import random
import logging

logger = logging.getLogger(__name__)

def get_similar_games(db: Session, game_id: int, limit: int = 5) -> List[Game]:
    """
    Encuentra juegos similares basados en géneros y etiquetas compartidas
    """
    try:
        # Obtener el juego base
        base_game = db.query(Game).filter(Game.id == game_id).first()
        if not base_game:
            return []
            
        # Encontrar juegos con géneros o etiquetas similares
        base_genres = set(base_game.genres) if base_game.genres else set()
        base_tags = set(base_game.tags) if base_game.tags else set()
        
        # Query para encontrar juegos similares
        similar_games = db.query(Game).filter(
            (Game.id != game_id) &  # Excluir el juego actual
            (
                # Juegos que comparten géneros o tags
                (Game.genres.overlap(base_genres)) |
                (Game.tags.overlap(base_tags))
            )
        ).limit(limit).all()
        
        return similar_games
    except Exception as e:
        logger.error(f"Error al buscar juegos similares: {e}")
        return []

def get_recommendations_for_user(db: Session, user: User, limit: int = 10) -> List[Game]:
    """
    Genera recomendaciones personalizadas basadas en las preferencias del usuario
    """
    try:
        # Filtrar por precio máximo del usuario si está definido
        query = db.query(Game)
        
        if user.max_price is not None:
            query = query.filter(Game.price <= user.max_price)
            
        # Filtrar por géneros preferidos si el usuario los ha definido
        if user.preferred_genres:
            query = query.filter(Game.genres.overlap(user.preferred_genres))
            
        # Obtener juegos aleatorios que cumplan los criterios
        total_games = query.count()
        
        if total_games <= limit:
            return query.all()
        else:
            # Seleccionar aleatoriamente para evitar mostrar siempre los mismos
            random_offset = random.randint(0, max(0, total_games - limit))
            return query.offset(random_offset).limit(limit).all()
            
    except Exception as e:
        logger.error(f"Error al generar recomendaciones: {e}")
        return []

def get_hidden_gems(db: Session, limit: int = 10) -> List[Game]:
    """
    Encuentra juegos 'joya escondida' (bien valorados pero poco conocidos)
    """
    try:
        # Filtrar juegos indie con buena valoración pero pocas reseñas
        gems = db.query(Game).filter(
            Game.tags.contains(['indie']) &  # Es un juego indie
            (Game.rating >= 4.0) &  # Buena valoración
            (Game.reviews_count < 1000)  # Relativamente desconocido
        ).limit(limit).all()
        
        return gems
    except Exception as e:
        logger.error(f"Error al buscar hidden gems: {e}")
        return []
