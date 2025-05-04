from fastapi import APIRouter, Depends, HTTPException
from ..utils.rawg_api import rawg_api

router = APIRouter(
    prefix="/genres",
    tags=["genres"],
)

@router.get("/")
def get_genres():
    """
    Obtiene la lista de géneros disponibles.
    """
    try:
        return rawg_api.get_genres()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Error al obtener géneros: {str(e)}")
