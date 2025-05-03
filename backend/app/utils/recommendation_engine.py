from sqlalchemy.orm import Session
from collections import Counter
from typing import List, Dict, Any
import logging
from .. import models

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Motor de recomendaciones para sugerir juegos indies a usuarios"""
    
    def __init__(self):
        """Inicializa el motor de recomendaciones"""
        pass
    
    def get_genre_preferences(self, user_id: int, db: Session) -> Dict[str, float]:
        """
        Obtiene las preferencias de géneros del usuario basadas en sus juegos favoritos
        
        Args:
            user_id: ID del usuario
            db: Sesión de base de datos
            
        Returns:
            Diccionario con los géneros como claves y su puntuación como valores
        """
        try:
            # Obtener el usuario con sus juegos favoritos
            user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
            
            if not user or not user.juegos_favoritos:
                logger.warning(f"Usuario {user_id} no encontrado o sin juegos favoritos")
                return {}
            
            # Extraer todos los géneros de los juegos favoritos
            all_genres = []
            for game in user.juegos_favoritos:
                all_genres.extend(game.generos)
            
            # Contar frecuencia de cada género
            genre_counts = Counter(all_genres)
            total_genres = sum(genre_counts.values())
            
            # Normalizar para obtener pesos
            genre_weights = {genre: count/total_genres for genre, count in genre_counts.items()}
            
            logger.info(f"Preferencias de géneros para usuario {user_id}: {genre_weights}")
            return genre_weights
            
        except Exception as e:
            logger.error(f"Error obteniendo preferencias de géneros: {str(e)}")
            return {}
    
    def calculate_game_score(self, game, genre_preferences: Dict[str, float]) -> float:
        """
        Calcula la puntuación de un juego basado en las preferencias del usuario
        
        Args:
            game: Objeto juego de la base de datos
            genre_preferences: Diccionario con preferencias de géneros
            
        Returns:
            Puntuación del juego (mayor es mejor match)
        """
        if not genre_preferences:
            return 0.0
        
        score = 0.0
        
        # Sumar puntuación por cada género que coincide con las preferencias
        for genre in game.generos:
            if genre in genre_preferences:
                score += genre_preferences[genre]
        
        return score
    
    def recommend_games(self, user_id: int, max_price: float = None, limit: int = 10, db: Session = None) -> List[Dict[str, Any]]:
        """
        Recomienda juegos a un usuario basado en sus preferencias
        
        Args:
            user_id: ID del usuario
            max_price: Precio máximo para filtrar juegos (si es None, usa el del usuario)
            limit: Número máximo de recomendaciones
            db: Sesión de base de datos
            
        Returns:
            Lista de juegos recomendados con puntuación
        """
        try:
            # Obtener usuario si no se ha especificado precio máximo
            user = None
            if max_price is None:
                user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
                if not user:
                    logger.warning(f"Usuario {user_id} no encontrado")
                    return []
                max_price = user.precio_max
            
            # Obtener preferencias de géneros
            genre_preferences = self.get_genre_preferences(user_id, db)
            
            if not genre_preferences:
                logger.warning(f"No se pudieron determinar preferencias para usuario {user_id}")
                return []
            
            # Obtener juegos de la base de datos que estén dentro del presupuesto
            query = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones)
            
            if max_price is not None and max_price > 0:
                query = query.filter(models.JuegosScrapeadoDeSteamParaRecomendaiones.precio <= max_price)
            
            potential_games = query.all()
            
            if not potential_games:
                logger.warning(f"No se encontraron juegos dentro del presupuesto {max_price}")
                return []
            
            # Calcular puntuación para cada juego
            scored_games = []
            for game in potential_games:
                # Si el usuario ya tiene juegos favoritos, evitar recomendar los mismos
                if user and user.juegos_favoritos:
                    if any(favorite.nombre == game.nombre for favorite in user.juegos_favoritos):
                        continue
                
                score = self.calculate_game_score(game, genre_preferences)
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
            
            logger.info(f"Generadas {len(recommendations)} recomendaciones para usuario {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {str(e)}")
            return []

# Instancia global
recommendation_engine = RecommendationEngine()
