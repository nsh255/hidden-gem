import requests
import random
import time
import os
from typing import List, Dict, Any, Optional
import logging

class RawgApi:
    def __init__(self):
        """
        Inicializa la API de RAWG con la clave API obtenida de las variables de entorno.
        """
        # Obtener la clave API desde las variables de entorno o usar una predeterminada
        self.api_key = os.environ.get("RAWG_API_KEY", "your_default_api_key")
        self.base_url = "https://api.rawg.io/api"
        
    def get_games(self, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        Obtiene una lista paginada de juegos.
        
        Args:
            page: Número de página a recuperar
            page_size: Número de juegos por página
            
        Returns:
            Diccionario con la respuesta de la API o None si hay un error
        """
        try:
            url = f"{self.base_url}/games"
            params = {
                "key": self.api_key,
                "page": page,
                "page_size": page_size
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error al obtener juegos: {str(e)}")
            return None
    
    def search_games(self, query: str, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        Busca juegos por nombre.
        
        Args:
            query: Texto de búsqueda
            page: Número de página a recuperar
            page_size: Número de juegos por página
            
        Returns:
            Diccionario con resultados de búsqueda o None si hay un error
        """
        try:
            url = f"{self.base_url}/games"
            params = {
                "key": self.api_key,
                "search": query,
                "page": page,
                "page_size": page_size
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error al buscar juegos: {str(e)}")
            return None
    
    def get_game(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un juego específico.
        
        Args:
            game_id: ID del juego en la API de RAWG
            
        Returns:
            Diccionario con los detalles del juego o None si hay un error
        """
        try:
            url = f"{self.base_url}/games/{game_id}"
            params = {"key": self.api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error al obtener detalles del juego: {str(e)}")
            return None
    
    def get_game_screenshots(self, game_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene las capturas de pantalla de un juego específico.
        
        Args:
            game_id: ID del juego en la API de RAWG
            
        Returns:
            Lista de diccionarios con información de capturas de pantalla o None si hay un error
        """
        try:
            url = f"{self.base_url}/games/{game_id}/screenshots"
            params = {"key": self.api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            logging.error(f"Error al obtener capturas de pantalla: {str(e)}")
            return None
    
    def get_trending_games(self, page: int = 1, page_size: int = 20, max_pages: int = 1) -> Optional[Dict[str, Any]]:
        """
        Obtiene juegos en tendencia.
        
        Args:
            page: Número de página inicial
            page_size: Número de juegos por página
            max_pages: Número máximo de páginas a recuperar
            
        Returns:
            Diccionario con juegos en tendencia combinados de múltiples páginas o None si hay un error
        """
        try:
            all_results = []
            total_count = 0
            next_page = None
            
            for current_page in range(page, page + max_pages):
                url = f"{self.base_url}/games"
                params = {
                    "key": self.api_key,
                    "ordering": "-added",  # Ordenar por más recientemente añadidos
                    "page": current_page,
                    "page_size": page_size
                }
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                all_results.extend(data.get("results", []))
                
                if current_page == page:  # Solo en la primera página
                    total_count = data.get("count", 0)
                    next_page = data.get("next")
                
                if not data.get("next"):
                    break
                    
                # Esperar un poco para no sobrecargar la API
                time.sleep(0.2)
            
            return {
                "count": total_count,
                "next": next_page,
                "results": all_results
            }
        except Exception as e:
            logging.error(f"Error al obtener juegos en tendencia: {str(e)}")
            return None
    
    def get_random_games(self, count: int = 10) -> Optional[Dict[str, Any]]:
        """
        Obtiene una selección aleatoria de juegos.
        
        Args:
            count: Número de juegos aleatorios a obtener
            
        Returns:
            Diccionario con juegos aleatorios o None si hay un error
        """
        try:
            # Obtener juegos de páginas aleatorias
            max_page = 100  # Asumir que hay al menos 100 páginas
            games = []
            
            # Hacer varias solicitudes para obtener diferentes juegos
            attempts = min(5, (count // 5) + 1)  # Limitar el número de intentos
            
            for _ in range(attempts):
                random_page = random.randint(1, max_page)
                url = f"{self.base_url}/games"
                params = {
                    "key": self.api_key,
                    "page": random_page,
                    "page_size": 20
                }
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("results"):
                    games.extend(data.get("results", []))
                
                # Esperar un poco para no sobrecargar la API
                time.sleep(0.2)
                
                if len(games) >= count:
                    break
            
            # Mezclar y limitar al número solicitado
            random.shuffle(games)
            games = games[:count]
            
            return {
                "count": len(games),
                "results": games
            }
        except Exception as e:
            logging.error(f"Error al obtener juegos aleatorios: {str(e)}")
            return None
    
    def get_games_by_genre(self, genre_id: int, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        Obtiene juegos filtrados por género.
        
        Args:
            genre_id: ID del género para filtrar
            page: Número de página a recuperar
            page_size: Número de juegos por página
            
        Returns:
            Diccionario con juegos del género especificado o None si hay un error
        """
        try:
            url = f"{self.base_url}/games"
            params = {
                "key": self.api_key,
                "genres": genre_id,
                "page": page,
                "page_size": page_size
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error al obtener juegos por género: {str(e)}")
            return None
    
    def get_games_by_genres(self, genre_slugs: List[str], page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        Obtiene juegos filtrados por varios géneros (usando slugs).
        
        Args:
            genre_slugs: Lista de slugs de géneros para filtrar
            page: Número de página a recuperar
            page_size: Número de juegos por página
            
        Returns:
            Diccionario con juegos que coincidan con los géneros o None si hay un error
        """
        try:
            url = f"{self.base_url}/games"
            params = {
                "key": self.api_key,
                "genres": ",".join(genre_slugs),
                "page": page,
                "page_size": page_size
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error al obtener juegos por géneros: {str(e)}")
            return None
    
    def get_games_with_filters(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Obtiene juegos con filtros personalizados.
        
        Args:
            params: Diccionario con parámetros de filtrado para la API
            
        Returns:
            Diccionario con juegos filtrados o None si hay un error
        """
        try:
            url = f"{self.base_url}/games"
            # Agregar la clave API a los parámetros
            filter_params = params.copy()
            filter_params["key"] = self.api_key
            
            response = requests.get(url, params=filter_params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error al obtener juegos filtrados: {str(e)}")
            return None
    
    def get_genres(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene la lista de géneros disponibles.
        
        Returns:
            Diccionario con géneros disponibles o None si hay un error
        """
        try:
            url = f"{self.base_url}/genres"
            params = {"key": self.api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error al obtener géneros: {str(e)}")
            return None

# Crear una instancia para usar en toda la aplicación
rawg_api = RawgApi()
