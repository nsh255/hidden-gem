from pydantic import BaseModel, AnyHttpUrl, Field
from typing import List, Optional

class GameBase(BaseModel):
    title: str
    price: float = Field(ge=0.0)  # El precio debe ser mayor o igual a 0
    genres: str  # Géneros como texto separado por comas
    tags: str    # Tags como texto separado por comas
    url: AnyHttpUrl
    description: Optional[str] = None
    is_indie: bool = True
    source: str  # "rawg" o "steam"

class GameCreate(GameBase):
    pass

class GameOut(GameBase):
    id: int
    
    class Config:
        orm_mode = True  # Permite convertir un modelo SQLAlchemy en un modelo Pydantic

class GameInDB(GameOut):
    pass

class GameWithFavorites(GameOut):
    favorited_by: List['UserOut'] = []

# Para evitar referencia circular
from .user import UserOut
GameWithFavorites.update_forward_refs()
