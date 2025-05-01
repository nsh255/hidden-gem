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

class GameSearch(BaseModel):
    text: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    sort_by: Optional[str] = "name"  # Opciones: name, price_asc, price_desc, rating
    skip: int = 0
    limit: int = 50

# Para evitar referencia circular
from .user import UserOut
GameWithFavorites.update_forward_refs()
