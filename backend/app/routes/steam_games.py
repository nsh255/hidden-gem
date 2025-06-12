from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..database import get_db
from .. import models, schemas
from ..utils.steam_scraper import steam_scraper
from ..utils.google_ai import classify_games_sexual_content
from pydantic import BaseModel
import logging
import json

router = APIRouter(
    prefix="/steam-games",
    tags=["steam-games"],
)

class SteamAIRequest(BaseModel):
    user_id: int

@router.post("/", response_model=schemas.JuegoSteam, status_code=status.HTTP_201_CREATED)
def create_steam_game(game: schemas.JuegoSteamCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo juego de Steam en la base de datos.

    - **game**: Datos del juego a crear
    - **db**: Sesión de la base de datos

    Returns:
        El juego creado.
    """
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
    """
    Obtiene una lista de juegos de Steam desde la base de datos.

    - **skip**: Número de registros a omitir
    - **limit**: Número máximo de registros a devolver
    - **db**: Sesión de la base de datos

    Returns:
        Lista de juegos de Steam.
    """
    games = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).offset(skip).limit(limit).all()
    return games

@router.get("/{game_id}", response_model=schemas.JuegoSteam)
def read_steam_game(game_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un juego de Steam por su ID.

    - **game_id**: ID del juego
    - **db**: Sesión de la base de datos

    Returns:
        Detalles del juego.
    """
    game = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).filter(
        models.JuegosScrapeadoDeSteamParaRecomendaiones.id == game_id
    ).first()
    
    if game is None:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_steam_game(game_id: int, db: Session = Depends(get_db)):
    """
    Elimina un juego de Steam de la base de datos.

    - **game_id**: ID del juego a eliminar
    - **db**: Sesión de la base de datos

    Returns:
        None.
    """
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
    min_new_games: int = Query(100, description="Número mínimo de juegos NUEVOS a añadir"),
    db: Session = Depends(get_db)
):
    """
    Scrapea juegos indies de Steam de forma masiva y los guarda en la base de datos.

    - **min_new_games**: Número mínimo de juegos nuevos a añadir
    - **db**: Sesión de la base de datos

    Returns:
        Estadísticas del proceso de scraping.
    """
    """
    Scrapea juegos indies de Steam de forma masiva y sincrónica.
    
    Este endpoint inicia un proceso sincrónico para scrapear juegos indies de Steam
    directamente desde la página web (no usa API).
    
    Características:
    - Scrapea juegos que aparecen en la página de tags de Indie de Steam
    - Asegura que se añadan al menos el número mínimo de juegos NUEVOS especificado
    - Filtra automáticamente juegos que ya existen en la base de datos
    - Asegura que tengan el tag "Indie"
    - Excluye juegos con tags de contenido adulto ("Sexual Content", "Nudity", etc.)
    - Almacena los juegos en la base de datos para recomendaciones
    
    Nota: Este es un proceso sincrónico que puede tardar varios minutos.
    Para bases de datos grandes se recomienda ejecutar en horario de bajo tráfico.
    
    Returns:
        Estadísticas del proceso de scraping y número de juegos añadidos a la BD
    """
    try:
        # Obtener los nombres de juegos que ya existen en la BD para evitar duplicados
        existing_games = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones.nombre).all()
        existing_names = [game[0] for game in existing_games]
        
        logging.info(f"Ya existen {len(existing_names)} juegos en la base de datos")
        
        # Iniciar el scraping, pasándole la lista de nombres existentes
        logging.info(f"Iniciando scraping de al menos {min_new_games} juegos NUEVOS desde la web de Steam...")
        scrape_results = steam_scraper.scrape_bulk_indie_games(
            min_new_games=min_new_games, 
            existing_names=existing_names
        )
        
        games_to_add = scrape_results["results"]
        stats = scrape_results["stats"]
        
        if len(games_to_add) == 0:
            return {
                "status": "warning",
                "message": "No se encontraron juegos nuevos para añadir",
                "estadisticas_scraping": stats,
                "juegos_nuevos": 0,
                "juegos_actuales": len(existing_names)
            }
        
        # Contar juegos añadidos con éxito
        added_count = 0
        
        # Añadir juegos a la base de datos en lotes para mejor rendimiento
        batch_size = 50
        for i in range(0, len(games_to_add), batch_size):
            batch = games_to_add[i:i+batch_size]
            
            for game_data in batch:
                try:
                    # Crear nuevo juego en la BD
                    new_game = models.JuegosScrapeadoDeSteamParaRecomendaiones(**game_data)
                    db.add(new_game)
                    added_count += 1
                        
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

    - **db**: Sesión de la base de datos

    Returns:
        Número de juegos en la base de datos.
    """
    """
    Obtiene el número actual de juegos de Steam en la base de datos.
    
    Returns:
        Número de juegos en la base de datos
    """
    count = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).count()
    return {"count": count}

@router.post("/recommend-steam-ai", response_model=List[schemas.JuegoSteam])
def recommend_steam_games_ai(
    req: SteamAIRequest,
    db: Session = Depends(get_db)
):
    """
    Recomienda juegos de Steam usando la IA de Google a partir de los juegos favoritos del usuario.
    """
    user_id = req.user_id
    # Obtener juegos favoritos del usuario
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user or not user.juegos_favoritos:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o sin favoritos")
    fav_games = [{"name": g.nombre, "description": g.descripcion} for g in user.juegos_favoritos]

    # Obtener todos los juegos de Steam
    steam_games = db.query(models.JuegosScrapeadoDeSteamParaRecomendaiones).all()
    if not steam_games:
        return []

    # Preparamos los juegos candidatos para la IA
    candidates = [{"id": g.id, "name": g.nombre, "description": g.descripcion} for g in steam_games]

    # Prompt para la IA: recomendar juegos de la lista de Steam que mejor encajen con los favoritos
    prompt = (
        "Te paso dos listas de juegos en formato JSON. "
        "La primera lista son los juegos favoritos del usuario. "
        "La segunda lista son juegos candidatos de Steam. "
        "Devuélveme una lista JSON de exactamente 10 IDs de los juegos candidatos que más recomendarías al usuario, "
        "basado en similitud de género, temática y descripción. "
        "Si no hay suficientes coincidencias, rellena la lista con IDs aleatorios de los candidatos. "
        "Solo responde la lista JSON de IDs, nada más. Ejemplo: [12, 34, 56, 78, 90, 123, 456, 789, 1011, 1213]\n"
        "Favoritos: " + json.dumps(fav_games, ensure_ascii=False) + "\n"
        "Candidatos: " + json.dumps(candidates, ensure_ascii=False)
    )
    # Llamada a la IA
    import os, requests
    GOOGLE_AI_API_KEY = os.environ.get("GOOGLE_AI_API_KEY")
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"  # <-- FIXED URL
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": GOOGLE_AI_API_KEY}
    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=60)
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        # Extraer la primera lista de números del texto
        start = text.find('[')
        end = text.find(']', start)
        if start != -1 and end != -1:
            json_str = text[start:end+1]
            try:
                ids = json.loads(json_str)
                if not isinstance(ids, list):
                    ids = []
            except Exception:
                ids = []
        else:
            ids = []
    except Exception as e:
        ids = []
    # Fallback: si la IA no devuelve nada, devolver 10 juegos aleatorios
    if not ids:
        import random
        ids = [g.id for g in random.sample(steam_games, min(10, len(steam_games)))]
    # Buscar los juegos por ID
    recommended = [g for g in steam_games if g.id in ids]
    return recommended
