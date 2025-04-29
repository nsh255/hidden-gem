from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr
    nickname: str
    max_price: float = Field(ge=0.0)  # Debe ser mayor o igual a 0

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    profile_pic: Optional[str] = None
    
    class Config:
        orm_mode = True  # Permite convertir un modelo SQLAlchemy en un modelo Pydantic

class UserWithFavorites(UserOut):
    favorite_games: List['GameOut'] = []

# Para evitar referencia circular
from .game import GameOut
UserWithFavorites.update_forward_refs()
