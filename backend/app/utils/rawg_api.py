import requests
import random
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

    def get_trending_games(self, page=1, page_size=20, max_pages=1):
        """
        Get popular or trending games
        
        Args:
            page: Starting page number
            page_size: Number of games per page
            max_pages: Number of pages to retrieve (for collecting more games)
        
        Returns:
            Dictionary with trending games data, merged from multiple pages if max_pages > 1
        """
        all_results = []
        
        for current_page in range(page, page + max_pages):
            url = f"{self.BASE_URL}/games"
            params = {
                'key': self.api_key,
                'ordering': '-added',  # Order by popularity
                'page': current_page,
                'page_size': page_size
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'results' in data:
                    all_results.extend(data['results'])
                    
                # If we've reached the last page, break the loop
                if current_page >= data.get('count', 0) // page_size:
                    break
                    
            except requests.RequestException as e:
                logger.error(f"Error fetching trending games from RAWG: {e}")
                # Return what we have so far if there's an error
                if all_results:
                    return {"results": all_results, "count": len(all_results)}
                return None
        
        return {"results": all_results, "count": len(all_results)}
    
    def get_random_games(self, count=10):
        """
        Get random games from RAWG API
        
        This method fetches games from random pages to provide variety.
        
        Args:
            count: Number of random games to retrieve
        
        Returns:
            Dictionary with random games data
        """
        # Fetch approximate count of all games first
        try:
            url = f"{self.BASE_URL}/games"
            params = {'key': self.api_key, 'page_size': 1}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            total_games = data.get('count', 10000)  # Use 10000 as fallback
            max_page = min(500, total_games // 20)  # RAWG API limits pages to 500
            
            # Select random pages to get games
            random_pages = [random.randint(1, max_page) for _ in range(count // 20 + 1)]
            all_results = []
            
            for page in random_pages:
                params = {
                    'key': self.api_key,
                    'page': page,
                    'page_size': 20
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                page_data = response.json()
                
                if 'results' in page_data:
                    all_results.extend(page_data['results'])
            
            # Shuffle and limit to requested count
            random.shuffle(all_results)
            return {"results": all_results[:count], "count": min(count, len(all_results))}
            
        except requests.RequestException as e:
            logger.error(f"Error fetching random games from RAWG: {e}")
            return None

# Crear una instancia para importar en otros módulos
rawg_api = RawgAPI()
