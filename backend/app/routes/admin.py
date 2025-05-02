from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from random import sample
import subprocess
from pathlib import Path
import os
import logging
import sys
import time

from app.database import get_db
from app.models.game import Game
from app.schemas.game import GameOut
from app.services.rawg_api import search_games, get_game_details, get_genres

router = APIRouter()
logger = logging.getLogger(__name__)

# Endpoints administrativos para juegos
@router.get("/games", response_model=List[GameOut])
async def admin_get_all_games(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los juegos sin autenticación (modo admin)
    """
    db_games = db.query(Game).offset(skip).limit(limit).all()
    
    # Explicitly convert ORM models to Pydantic models
    games = []
    for game in db_games:
        game_data = {
            "id": game.id,
            "title": game.title,
            "price": game.price,
            "genres": game.genres,  # Ensure this is a list
            "tags": game.tags,      # Ensure this is a list
            "url": game.url,
            "description": game.description,
            "is_indie": game.is_indie,
            "source": game.source
        }
        games.append(GameOut(**game_data))
    
    return games

@router.get("/games/{game_id}", response_model=GameOut)
async def admin_get_game(
    game_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un juego específico por ID sin autenticación (modo admin)
    """
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return game

# Endpoints administrativos para el scraper
@router.post("/scraper/run-spider", status_code=202)
async def admin_run_spider(
    background_tasks: BackgroundTasks, 
    max_pages: int = Query(20, description="Número máximo de páginas a scrapear por categoría")
):
    """
    Ejecuta el spider de Steam en segundo plano (modo admin)
    """
    def execute_spider():
        try:
            # Obtiene el directorio raíz del proyecto
            project_dir = Path(__file__).parent.parent.parent
            os.chdir(project_dir)
            
            logger.info(f"[ADMIN] Ejecutando spider desde: {os.getcwd()}")
            
            # Ejecuta el spider usando crawl en lugar de runspider
            cmd = [
                sys.executable, 
                "-m", 
                "scrapy", 
                "crawl", 
                "games_spider",
                "-s", f"CLOSESPIDER_PAGECOUNT={max_pages}",
                "-a", "max_games=2000",
                "--logfile=admin_spider_log.txt",
                "-s", "LOG_LEVEL=DEBUG"
            ]
            
            logger.info(f"[ADMIN] Ejecutando comando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": str(project_dir)}
            )
            
            if result.returncode != 0:
                logger.error(f"[ADMIN] Error al ejecutar el spider: {result.stderr}")
                with open("admin_spider_error.log", "w") as f:
                    f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
                logger.info("[ADMIN] Error guardado en admin_spider_error.log")
            else:
                logger.info("[ADMIN] Spider ejecutado correctamente")
                with open("admin_spider_output.log", "w") as f:
                    f.write(result.stdout)
                logger.info("[ADMIN] Salida guardada en admin_spider_output.log")
                
        except Exception as e:
            logger.exception(f"[ADMIN] Error inesperado al ejecutar el spider: {str(e)}")
    
    background_tasks.add_task(execute_spider)
    return {"message": "Spider iniciado en segundo plano (modo admin)"}

@router.post("/scraper/run")
async def admin_execute_spider_sync(
    max_pages: int = Query(100, description="Número máximo de páginas a scrapear"),
    max_games: int = Query(2000, description="Número máximo de juegos a extraer")
):
    """
    Ejecuta el spider de forma síncrona (modo admin)
    """
    try:
        start_time = time.time()
        logger.info(f"[ADMIN] Ejecutando spider desde: {os.getcwd()}")
        
        cmd = [
            "python", 
            "-m", 
            "scrapy", 
            "crawl", 
            "games_spider",
            "-s", f"CLOSESPIDER_PAGECOUNT={max_pages}",
            "-a", f"max_games={max_games}",
            "-s", "LOG_LEVEL=DEBUG"
        ]
        
        logger.info(f"[ADMIN] Ejecutando comando: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ}
        )
        
        # Guardar logs completos independientemente del resultado
        with open("admin_spider_debug.log", "w") as f:
            f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
        
        if result.returncode != 0:
            logger.error(f"[ADMIN] Error al ejecutar el spider: {result.stderr}")
            return {
                "success": False,
                "message": "Error al ejecutar el spider (modo admin)",
                "error": result.stderr,
                "output": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                "cwd": os.getcwd(),
                "execution_time": f"{time.time() - start_time:.2f} segundos"
            }
        else:
            logger.info("[ADMIN] Spider ejecutado correctamente")
            return {
                "success": True,
                "message": "Spider ejecutado correctamente (modo admin)",
                "output": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                "execution_time": f"{time.time() - start_time:.2f} segundos"
            }
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"[ADMIN] Error inesperado al ejecutar el spider: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar el spider (modo admin): {error_msg}"
        )

# Endpoints administrativos para recomendaciones aleatorias
@router.get("/recommendations/random", response_model=List[GameOut])
async def admin_get_random_recommendations(
    limit: int = Query(10, description="Número de juegos a recomendar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene recomendaciones aleatorias sin autenticación (modo admin)
    
    En lugar de usar un algoritmo de recomendación basado en preferencias del usuario,
    simplemente devuelve juegos aleatorios de la base de datos.
    """
    # Obtener el número total de juegos en la base de datos
    total_games = db.query(Game).count()
    
    # Si hay menos juegos que el límite solicitado, ajustar el límite
    if total_games < limit:
        limit = total_games
    
    if limit == 0:
        return []
    
    # Obtener IDs de todos los juegos
    game_ids = [game_id for (game_id,) in db.query(Game.id).all()]
    
    # Seleccionar IDs aleatorios
    if len(game_ids) > limit:
        selected_ids = sample(game_ids, limit)
    else:
        selected_ids = game_ids
    
    # Obtener los juegos correspondientes a los IDs seleccionados
    random_games = db.query(Game).filter(Game.id.in_(selected_ids)).all()
    
    return random_games

# Endpoints administrativos para RAWG API
@router.get("/rawg/search")
async def admin_search_rawg_games(
    genres: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Busca juegos en la API de RAWG sin autenticación (modo admin)
    """
    try:
        games = search_games(genres=genres)
        return {"games": games}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar juegos (modo admin): {str(e)}")

@router.get("/rawg/genres")
async def admin_list_genres(
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de géneros disponibles en RAWG sin autenticación (modo admin)
    """
    try:
        genres = get_genres()
        return {"genres": genres}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener géneros (modo admin): {str(e)}")

@router.get("/rawg/details/{game_id}")
async def admin_get_rawg_game_details(
    game_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene detalles completos de un juego específico desde RAWG sin autenticación (modo admin)
    """
    try:
        game = get_game_details(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return game
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalles del juego (modo admin): {str(e)}")
