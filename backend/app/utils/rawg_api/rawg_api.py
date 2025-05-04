from typing import List

def get_games(page: int = 1, page_size: int = 20) -> dict:
    """
    Obtiene una lista de juegos.
    """
    try:
        # Implementación para obtener juegos
        # Esto es una simulación, en una implementación real,
        # se haría una petición a la API de RAWG
        return {
            "count": 100,
            "next": f"https://api.rawg.io/api/games?page={page + 1}",
            "previous": f"https://api.rawg.io/api/games?page={page - 1}" if page > 1 else None,
            "results": [
                {"id": i, "name": f"Game {i}", "released": "2021-01-01", "rating": 4.5}
                for i in range((page - 1) * page_size, page * page_size)
            ]
        }
    except Exception as e:
        print(f"Error obteniendo juegos: {str(e)}")
        return {"count": 0, "next": None, "previous": None, "results": []}

def get_game_screenshots(game_id: int) -> List[dict]:
    """
    Obtiene las capturas de pantalla de un juego específico.
    """
    try:
        # Implementación para obtener capturas de pantalla
        # Esto es una simulación, en una implementación real,
        # se haría una petición a la API de RAWG
        return [
            {"id": 1, "image": f"https://placekitten.com/800/450?image={i}"} 
            for i in range(1, 6)
        ]
    except Exception as e:
        print(f"Error obteniendo capturas: {str(e)}")
        return []

def get_games_by_genre(genre_id: int, page: int = 1, page_size: int = 20) -> dict:
    """
    Obtiene juegos filtrados por un género específico.
    """
    try:
        # Implementación para obtener juegos por género
        # Similar a get_games pero con filtro de género
        result = get_games(page, page_size)
        # Simular filtro (en una implementación real, se pasaría el filtro a la API)
        return result
    except Exception as e:
        print(f"Error obteniendo juegos por género: {str(e)}")
        return {"count": 0, "next": None, "previous": None, "results": []}

def get_games_by_genres(genre_ids: List[int], page: int = 1, page_size: int = 20) -> dict:
    """
    Obtiene juegos filtrados por múltiples géneros.
    """
    try:
        # Implementación similar a get_games_by_genre pero con múltiples géneros
        result = get_games(page, page_size)
        return result
    except Exception as e:
        print(f"Error obteniendo juegos por géneros: {str(e)}")
        return {"count": 0, "next": None, "previous": None, "results": []}

def search_games_by_genres(genres: List[str], page: int = 1, page_size: int = 20) -> dict:
    """
    Busca juegos por nombres de géneros en lugar de IDs.
    """
    try:
        # Implementación similar a get_games_by_genres pero con nombres
        result = get_games(page, page_size)
        return result
    except Exception as e:
        print(f"Error buscando juegos por géneros: {str(e)}")
        return {"count": 0, "next": None, "previous": None, "results": []}

def get_genres() -> List[dict]:
    """
    Obtiene la lista de géneros disponibles.
    """
    try:
        # Implementación para obtener géneros
        # Esto es una simulación
        return [
            {"id": 1, "name": "Action"},
            {"id": 2, "name": "Adventure"},
            {"id": 3, "name": "RPG"},
            {"id": 4, "name": "Strategy"},
            {"id": 5, "name": "Shooter"},
            {"id": 6, "name": "Puzzle"},
            {"id": 7, "name": "Racing"},
            {"id": 8, "name": "Sports"},
            {"id": 9, "name": "Platformer"},
            {"id": 10, "name": "Simulation"}
        ]
    except Exception as e:
        print(f"Error obteniendo géneros: {str(e)}")
        return []