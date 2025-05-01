import os
import requests
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Obtener la clave API desde las variables de entorno
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
if not RAWG_API_KEY:
    logger.warning("RAWG_API_KEY no encontrada en .env. Añade RAWG_API_KEY=tu_clave_api_aqui en tu archivo .env")

# URL base para la API de RAWG
RAWG_BASE_URL = "https://api.rawg.io/api"

def search_games(genres: List[str] = None) -> List[Dict[str, Any]]:
    """
    Busca juegos en la API de RAWG por géneros opcionales.
    
    Args:
        genres (List[str], opcional): Lista de géneros para filtrar los juegos
        
    Returns:
        List[Dict[str, Any]]: Lista de juegos encontrados que cumplen los criterios
    
    Raises:
        ValueError: Si no se ha configurado RAWG_API_KEY
        requests.RequestException: Si hay un error en la solicitud HTTP
    """
    if not RAWG_API_KEY:
        raise ValueError("No se ha configurado RAWG_API_KEY en las variables de entorno")
    
    # Parámetros base para la consulta
    params = {
        "key": RAWG_API_KEY,
        "page_size": 40  # Número de resultados por página
    }
    
    # Añadir filtro de géneros si se proporciona
    if genres and len(genres) > 0:
        # RAWG utiliza IDs para los géneros, pero también acepta nombres
        params["genres"] = ",".join(genres)
    
    try:
        # Realizar la solicitud a la API de RAWG
        response = requests.get(f"{RAWG_BASE_URL}/games", params=params)
        response.raise_for_status()  # Lanza excepción si hay error HTTP
        
        data = response.json()
        results = data.get("results", [])
        
        formatted_games = []
        
        for game in results:
            # Intentar obtener información adicional del juego
            game_id = game.get("id")
            if game_id:
                game_details = get_game_details(game_id)
                
                # Añadir descripción al objeto del juego
                game["description"] = game_details.get("description_raw", "")
                
                # Adaptar el formato para nuestra aplicación
                formatted_game = format_game_data(game)
                formatted_games.append(formatted_game)
        
        return formatted_games
        
    except requests.RequestException as e:
        logger.error(f"Error al consultar la API de RAWG: {str(e)}")
        raise

def get_game_details(game_id: int) -> Dict[str, Any]:
    """
    Obtiene detalles adicionales de un juego específico por su ID.
    
    Args:
        game_id (int): ID del juego en RAWG
        
    Returns:
        Dict[str, Any]: Detalles completos del juego
    """
    params = {"key": RAWG_API_KEY}
    
    try:
        response = requests.get(f"{RAWG_BASE_URL}/games/{game_id}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error al obtener detalles del juego {game_id}: {str(e)}")
        return {}

def format_game_data(game: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formatea los datos del juego en un formato compatible con nuestro modelo.
    
    Args:
        game (Dict[str, Any]): Datos del juego de RAWG
        
    Returns:
        Dict[str, Any]: Datos del juego formateados
    """
    # Extraer géneros como texto separado por comas
    genres = ",".join([g.get("name", "") for g in game.get("genres", [])])
    
    # Extraer tags (usando los juegos similares como tags)
    tags = ",".join([t.get("name", "") for t in game.get("tags", [])])
    
    # Determinar si es indie
    is_indie = any(g.get("slug") == "indie" for g in game.get("genres", []))
    
    # Crear URL para el juego
    game_url = f"https://rawg.io/games/{game.get('slug', '')}"
    
    return {
        "title": game.get("name", ""),
        "genres": genres,
        "tags": tags,
        "url": game_url,
        "description": game.get("description", ""),
        "is_indie": is_indie,
        "source": "rawg"
    }

def get_genres() -> List[Dict[str, Any]]:
    """
    Obtiene la lista de géneros disponibles en RAWG.
    
    Returns:
        List[Dict[str, Any]]: Lista de géneros
    """
    params = {"key": RAWG_API_KEY}
    
    try:
        response = requests.get(f"{RAWG_BASE_URL}/genres", params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException as e:
        logger.error(f"Error al obtener los géneros: {str(e)}")
        return []
