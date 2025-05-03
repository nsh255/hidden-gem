from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from .. import models, schemas
from ..utils.steam_scraper import steam_scraper
import logging

router = APIRouter(
    prefix="/steam-games",
    tags=["steam-games"],
)

@router.post("/", response_model=schemas.JuegoSteam, status_code=status.HTTP_201_CREATED)
def create_steam_game(game: schemas.JuegoSteamCreate, db: Session = Depends(get_db)):
    # Verificar si el juego ya existe
    db_game = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).filter(
        models.JuegosScrapeadoDeSteamParaRecomendaiones.nombre == game.nombre
    ).first()
    
    if db_game:
        raise HTTPException(status_code=400, detail="Juego ya registrado")
    
    # Crear nuevo juego
    db_game = models.JuegosScrapeadoDeSteamParaRecomendaiones(**game.dict())
    
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

@router.get("/", response_model=List[schemas.JuegoSteam])
def read_steam_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    games = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).offset(skip).limit(limit).all()
    return games

@router.get("/{game_id}", response_model=schemas.JuegoSteam)
def read_steam_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).filter(
        models.JuegosScrapeadoDeSteamParaRecomendaiones.id == game_id
    ).first()
    
    if game is None:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_steam_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).filter(
        models.JuegosScrapeadoDeSteamParaRecomendaiones.id == game_id
    ).first()
    
    if game is None:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    
    db.delete(game)
    db.commit()
    return None

@router.post("/scrape-bulk", status_code=status.HTTP_200_OK)
def scrape_bulk_steam_games(
    min_games: int = Query(1000, description="Número mínimo de juegos a scrapear"),
    db: Session = Depends(get_db)
):
    """
    Scrapea juegos indies de Steam de forma masiva y sincrónica.
    
    Este endpoint inicia un proceso sincrónico para scrapear juegos indies de Steam
    directamente desde la página web (no usa API).
    
    Características:
    - Scrapea juegos que aparecen en la página de tags de Indie de Steam
    - Asegura que tengan el tag "Indie"
    - Excluye juegos con tags de contenido adulto ("Sexual Content", "Nudity", etc.)
    - Almacena los juegos en la base de datos para recomendaciones
    - Continúa scrapeando hasta alcanzar el mínimo de juegos especificado
    
    Nota: Este es un proceso sincrónico que puede tardar varios minutos.
    Para bases de datos grandes se recomienda ejecutar en horario de bajo tráfico.
    
    Returns:
        Estadísticas del proceso de scraping y número de juegos añadidos a la BD
    """
    # Verificar cuántos juegos tenemos actualmente en la BD
    current_count = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).count()
    
    if current_count >= min_games:
        return {
            "status": "success",
            "message": f"Ya existen suficientes juegos en la base de datos: {current_count}",
            "juegos_actuales": current_count,
            "juegos_nuevos": 0
        }
    
    # Calcular cuántos juegos necesitamos scrapear
    games_needed = min_games - current_count
    
    try:
        # Iniciar el scraping
        logging.info(f"Iniciando scraping de al menos {games_needed} juegos nuevos desde la web de Steam...")
        scrape_results = steam_scraper.scrape_bulk_indie_games(min_games=games_needed)
        
        games_to_add = scrape_results["results"]
        stats = scrape_results["stats"]
        
        # Contar juegos añadidos con éxito
        added_count = 0
        duplicates_count = 0
        
        # Añadir juegos a la base de datos en lotes para mejor rendimiento
        batch_size = 50
        for i in range(0, len(games_to_add), batch_size):
            batch = games_to_add[i:i+batch_size]
            
            for game_data in batch:
                try:
                    # Verificar si el juego ya existe por nombre
                    existing_game = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).filter(
                        models.JuegosScrapeadoDeSteamParaRecomendaiones.nombre == game_data["nombre"]
                    ).first()
                    
                    if not existing_game:
                        # Crear nuevo juego en la BD
                        new_game = models.JuegosScrapeadoDeSteamParaRecomendaiones(
                            nombre=game_data["nombre"],
                            generos=game_data["generos"],
                            precio=game_data["precio"],
                            descripcion=game_data["descripcion"],
                            tags=game_data["tags"],
                            imagen_principal=game_data["imagen_principal"]
                        )
                        db.add(new_game)
                        added_count += 1
                    else:
                        duplicates_count += 1
                        
                except Exception as e:
                    logging.error(f"Error añadiendo juego {game_data.get('nombre', 'desconocido')}: {str(e)}")
            
            # Commit por lotes para evitar problemas de memoria
            db.commit()
            logging.info(f"Guardados {added_count} juegos en la base de datos hasta ahora")
        
        # Obtener el recuento final después de añadir juegos
        final_count = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).count()
        
        return {
            "status": "success",
            "message": f"Proceso de scraping completado. Añadidos {added_count} juegos nuevos.",
            "estadisticas_scraping": stats,
            "juegos_nuevos": added_count,
            "juegos_duplicados": duplicates_count,
            "juegos_actuales": final_count
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error en el proceso de scraping: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en el proceso de scraping: {str(e)}"
        )

@router.get("/count", status_code=status.HTTP_200_OK)
def get_steam_games_count(db: Session = Depends(get_db)):
    """
    Obtiene el número actual de juegos de Steam en la base de datos.
    
    Returns:
        Número de juegos en la base de datos
    """
    count = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).count()
    return {"count": count}
