import requests
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class RawgAPI:
    BASE_URL = "https://api.rawg.io/api"
    
    def __init__(self):
        self.api_key = settings.RAWG_API_KEY
        if not self.api_key:
            logger.warning("RAWG API key not set. Set RAWG_API_KEY in .env file.")
    
    def get_game(self, game_id):
        """Get a game by ID from RAWG API"""
        url = f"{self.BASE_URL}/games/{game_id}"
        params = {'key': self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching game from RAWG: {e}")
            return None
    
    def search_games(self, query, page=1, page_size=20):
        """Search for games by name"""
        url = f"{self.BASE_URL}/games"
        params = {
            'key': self.api_key,
            'search': query,
            'page': page,
            'page_size': page_size
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error searching games from RAWG: {e}")
            return None

    def get_trending_games(self, page=1, page_size=20):
        """Get popular or trending games"""
        url = f"{self.BASE_URL}/games"
        params = {
            'key': self.api_key,
            'ordering': '-added',  # Order by popularity
            'page': page,
            'page_size': page_size
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching trending games from RAWG: {e}")
            return None

# Crear una instancia para importar en otros módulos
rawg_api = RawgAPI()
