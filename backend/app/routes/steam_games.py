from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

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
