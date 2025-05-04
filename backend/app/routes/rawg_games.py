from fastapi import APIRouter, Depends, HTTPException, Query, status
import requests
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas
from ..utils.rawg_api import rawg_api

router = APIRouter(
    prefix="/rawg",
    tags=["rawg-games"],
)

@router.get("/search", response_model=dict)
def search_rawg_games(
    query: str = Query(..., description="Texto para buscar juegos"),
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(20, description="Elementos por página")
):
    """
    Busca juegos en la API de RAWG por nombre
    """
    result = rawg_api.search_games(query, page, page_size)
    if not result:
        raise HTTPException(status_code=503, detail="Error al conectar con RAWG API")
    
    # Filtrar juegos con contenido sexual en el título o descripción
    sexual_keywords = [
        "sexual", "nudity", "adult", "erotic", "porn", "hentai", "ecchi", 
        "fetish", "provocative", "explicit", "mature", "xxx", "nsfw", 
        "sensual", "seductive", "intimate", "suggestive", "lewd", "obscene"
    ]
    filtered_results = [
        game for game in result.get("results", [])
        if not any(keyword in (game.get("name", "").lower() + game.get("description", "").lower())
                   for keyword in sexual_keywords)
    ]
    result["results"] = filtered_results
    return result

@router.get("/game/{game_id}", response_model=dict)
def get_rawg_game(game_id: int):
    """
    Obtiene los detalles de un juego específico de RAWG por su ID
    """
    result = rawg_api.get_game(game_id)
    if not result:
        raise HTTPException(status_code=404, detail="Juego no encontrado o error en la API")
    
    # Verificar contenido sexual en el título o descripción
    sexual_keywords = [
        "sexual", "nudity", "adult", "erotic", "porn", "hentai", "ecchi", 
        "fetish", "provocative", "explicit", "mature", "xxx", "nsfw", 
        "sensual", "seductive", "intimate", "suggestive", "lewd", "obscene"
    ]
    if any(keyword in (result.get("name", "").lower() + result.get("description", "").lower())
           for keyword in sexual_keywords):
        raise HTTPException(status_code=400, detail="El juego contiene contenido inapropiado")
    
    return result

@router.post("/add-to-favorites", status_code=status.HTTP_201_CREATED, response_model=schemas.JuegoFavorito)
def add_rawg_game_to_favorites(
    user_id: int, 
    game_id: int,
    db: Session = Depends(get_db)
):
    """
    Añade un juego de RAWG a los favoritos del usuario, 
    creando primero el registro del juego si no existe
    """
    # Verificar que el usuario existe
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener datos del juego desde RAWG
    game_data = rawg_api.get_game(game_id)
    if not game_data:
        raise HTTPException(status_code=404, detail="Juego no encontrado en RAWG")
    
    # Verificar si el juego ya existe en la base de datos
    db_game = db.query(models.JuegosFavoritosDeUsuarioQueProvienenDeRawg).filter(
        models.JuegosFavoritosDeUsuarioQueProvienenDeRawg.nombre == game_data["name"]
    ).first()
    
    # Si no existe, crear el juego en la base de datos
    if not db_game:
        # Extraer géneros y tags
        generos = [genre["name"] for genre in game_data.get("genres", [])]
        tags = [tag["name"] for tag in game_data.get("tags", [])]
        
        # Crear objeto de juego
        db_game = models.JuegosFavoritosDeUsuarioQueProvienenDeRawg(
            nombre=game_data["name"],
            imagen=game_data.get("background_image", ""),
            descripcion=game_data.get("description", ""),
            generos=generos,
            tags=tags
        )
        
        db.add(db_game)
        db.commit()
        db.refresh(db_game)
    
    # Verificar si el juego ya es favorito del usuario
    if db_game in user.juegos_favoritos:
        raise HTTPException(
            status_code=400, 
            detail="Este juego ya está en la lista de favoritos del usuario"
        )
    
    # Añadir a favoritos
    user.juegos_favoritos.append(db_game)
    db.commit()
    
    return db_game

@router.get("/trending", response_model=dict)
def get_trending_games(
    page: int = Query(1, description="Número de página inicial"),
    page_size: int = Query(20, description="Elementos por página (máx. 40 recomendado)"),
    max_pages: int = Query(1, description="Número de páginas a recuperar (aumenta la cantidad de juegos)", ge=1, le=5)
):
    """
    Obtiene juegos populares o tendencia desde RAWG.
    
    Esta función permite recuperar más juegos en tendencia combinando resultados de múltiples páginas.
    
    - **page**: Página inicial para la búsqueda
    - **page_size**: Número de juegos por página (máximo recomendado: 40)
    - **max_pages**: Número de páginas a recuperar (1-5)
    
    Ejemplo: Para obtener 100 juegos en tendencia, puedes usar page_size=20 y max_pages=5
    """
    result = rawg_api.get_trending_games(page, page_size, max_pages)
    if not result:
        raise HTTPException(status_code=503, detail="Error al conectar con RAWG API")
    return result

@router.get("/random", response_model=dict)
def get_random_games(
    count: int = Query(10, description="Número de juegos aleatorios a recuperar", ge=1, le=50),
    _t: str = Query(None, description="Timestamp parameter to prevent caching")
):
    """
    Get truly random games by fetching from different pages and using different ordering methods
    """
    try:
        import random
        import time
        
        # Use current timestamp as part of seed to ensure different results each time
        current_seed = int(time.time() * 1000)
        random.seed(current_seed)
        print(f"Using random seed: {current_seed}")
        
        # Define various orderings to fetch different game sets
        orderings = [
            '-rating', 'rating', 
            '-released', 'released', 
            '-added', 'added',
            '-name', 'name',
            None  # Default ordering
        ]
        
        # Select a random ordering
        selected_ordering = random.choice(orderings)
        print(f"Selected ordering: {selected_ordering}")
        
        # Select random page numbers
        page_numbers = random.sample(range(1, 20), min(5, count))
        print(f"Selected pages: {page_numbers}")
        
        # Collect games from different pages with the selected ordering
        all_games = []
        for page in page_numbers:
            try:
                # Use RAWG API to fetch games with specific parameters
                params = {
                    'page': page,
                    'page_size': 20,
                }
                if selected_ordering:
                    params['ordering'] = selected_ordering
                    
                # Get games from RAWG API
                result = rawg_api.get_games_with_filters(params)
                
                if result and "results" in result and result["results"]:
                    all_games.extend(result["results"])
                    print(f"Added {len(result['results'])} games from page {page}")
            except Exception as e:
                print(f"Error fetching page {page}: {str(e)}")
                continue
        
        # If we didn't get enough games, try a fallback approach
        if len(all_games) < count:
            fallback_ordering = random.choice([o for o in orderings if o != selected_ordering and o is not None])
            try:
                fallback_result = rawg_api.get_games_with_filters({
                    'page': 1,
                    'page_size': 40,
                    'ordering': fallback_ordering
                })
                if fallback_result and "results" in fallback_result:
                    all_games.extend(fallback_result["results"])
                    print(f"Added {len(fallback_result['results'])} games from fallback")
            except Exception as e:
                print(f"Error with fallback: {str(e)}")
        
        # Make sure we have enough games
        if not all_games:
            print("No games found, using trending as last resort")
            try:
                trending = rawg_api.get_trending_games(1, count)
                if trending and "results" in trending:
                    all_games = trending["results"]
            except:
                return {"count": 0, "results": []}
        
        # Shuffle games thoroughly
        for _ in range(3):  # Shuffle multiple times
            random.shuffle(all_games)
            
        # Ensure each game gets a unique image URL by adding timestamp
        # and make sure we have different prices
        unique_games = []
        used_ids = set()
        
        for game in all_games:
            # Skip duplicates
            if game["id"] in used_ids:
                continue
                
            used_ids.add(game["id"])
            
            # Add random price
            base_price = 14.99
            rating_factor = game.get("rating", 0) / 5.0 if "rating" in game else 0.5
            random_factor = random.uniform(0.7, 1.3)  # More variation
            game["price"] = round((base_price + (10 * rating_factor)) * random_factor, 2)
            
            # Make image URL unique to prevent caching
            if "background_image" in game and game["background_image"]:
                unique_param = f"_t={current_seed}_{random.randint(1000, 9999)}"
                separator = "?" if "?" not in game["background_image"] else "&"
                game["background_image"] = f"{game['background_image']}{separator}{unique_param}"
            
            unique_games.append(game)
            
            # Stop once we have enough games
            if len(unique_games) >= count:
                break
        
        # Take only what we need
        final_games = unique_games[:count]
        print(f"Returning {len(final_games)} random games")
        
        return {"count": len(final_games), "results": final_games}
        
    except Exception as e:
        print(f"Random games error: {str(e)}")
        return {"count": 0, "results": []}

@router.get("/game/{game_id}/screenshots", response_model=List[dict])
def get_game_screenshots(game_id: int):
    """
    Obtiene las capturas de pantalla de un juego específico.
    """
    try:
        screenshots = rawg_api.get_game_screenshots(game_id)
        if not screenshots:
            return []
        return screenshots
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al obtener capturas: {str(e)}")
